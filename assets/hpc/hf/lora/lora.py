import json
import os
import subprocess

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from queue import Empty, PriorityQueue, Queue
from subprocess import CalledProcessError, Popen, TimeoutExpired
from threading import Condition, Event, Lock, Thread
from time import sleep
from typing import cast
from uuid import UUID


# current job
PBS_JOB_ID = os.environ['PBS_JOBID']

# squid proxy
HTTP_PROXY = 'http://10.150.1.1:3128'
HTTPS_PROXY = 'http://10.150.1.1:3128'

# paths
WORKDIR = Path('.')
ENV_PATH = Path('.env.hpc')
LORA_SIF_PATH = Path('lora.sif')
STATUS_TRACKER_PATH = Path(f'status_tracker_{PBS_JOB_ID}.json')
STATUS_TRACKER_TMP_PATH = STATUS_TRACKER_PATH.with_suffix('.tmp')

# path patterns
JOB_PATH_PATTERN = f'fine_tune_job_{PBS_JOB_ID}_*.json'

# thresholds
INACTIVE_THRESHOLD = timedelta(minutes=15)
WALL_TIME_THRESHOLD = timedelta(minutes=5)

basicConfig(level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
logger = getLogger(__name__)


class ProcessExitStatus(str, Enum):
    COMPLETED = 'completed'
    INTERRUPTED = 'interrupted'


class ProcessHandler:
    def __init__(self, *stop_events: Event):
        self._stop_events = stop_events
        self._process: Popen | None = None

    def wait(self, process: Popen) -> ProcessExitStatus:
        self._process = process
        DELAY = 15

        while self._process.poll() is None:
            if any(event.is_set() for event in self._stop_events):
                self._process.terminate()

                try:
                    self._process.wait(timeout=5)

                except TimeoutExpired:
                    self._process.kill()
                    self._process.wait()

                return ProcessExitStatus.INTERRUPTED

            sleep(DELAY)

        return_code = self._process.returncode

        if return_code != 0:
            raise CalledProcessError(return_code, self._process.args)

        return ProcessExitStatus.COMPLETED


@dataclass
class FineTuneJob:
    fine_tune_job_id: UUID
    timestamp: int


class FineTuneJobStatus(str, Enum):
    WAITING = 'waiting'
    RUNNING = 'running'
    FINISHED = 'finished'
    UNFINISHED = 'unfinished'


class FineTuneJobStatusTrackerResource:
    def __init__(self):
        self._waiting = Queue()
        self._lock = Lock()
        self._condition = Condition()

    def acquire(self):
        turn = object()

        with self._condition:
            self._waiting.put(turn)

            while self._waiting.queue[0] is not turn:
                self._condition.wait()

            self._lock.acquire()

    def release(self):
        with self._condition:
            self._lock.release()
            self._waiting.get()
            self._condition.notify_all()


class FineTuneJobStatusTracker:
    def __init__(
        self,
        is_status_update_allowed: bool = True,
        id_to_status: dict[UUID, FineTuneJobStatus] | None = None,
    ):
        self._is_status_update_allowed = is_status_update_allowed
        self._id_to_status = id_to_status or {}

    @property
    def is_status_update_allowed(self) -> bool:
        return self._is_status_update_allowed

    @is_status_update_allowed.setter
    def is_status_update_allowed(self, value: bool):
        self._is_status_update_allowed = value
        self._atomic_write()

    @property
    def id_to_status(self) -> dict[UUID, FineTuneJobStatus]:
        return self._id_to_status

    def get_status(self, id: UUID) -> FineTuneJobStatus | None:
        return self._id_to_status.get(id)

    def set_status(self, id: UUID, status: FineTuneJobStatus):
        if self._is_status_update_allowed:
            self._id_to_status[id] = status
            self._atomic_write()

    def _atomic_write(self):
        # locks prevent server-side (HPC) race conditions
        # atomic writing prevents client-side (math_rag app) race conditions
        with STATUS_TRACKER_TMP_PATH.open('w') as file:
            json_str = self.to_json()
            file.write(json_str)
            file.flush()
            os.fsync(file.fileno())

        os.replace(STATUS_TRACKER_TMP_PATH, STATUS_TRACKER_PATH)

    def to_json(self) -> str:
        json_dict = {
            'is_status_update_allowed': self._is_status_update_allowed,
            'id_to_status': {str(key): value.value for key, value in self._id_to_status.items()},
        }

        return json.dumps(json_dict)

    @staticmethod
    def from_json(json_str: str) -> 'FineTuneJobStatusTracker':
        json_dict = json.loads(json_str)

        return FineTuneJobStatusTracker(
            is_status_update_allowed=json_dict['is_status_update_allowed'],
            id_to_status={
                UUID(key): FineTuneJobStatus(value)
                for key, value in cast(dict, json_dict['id_to_status']).items()
            },
        )


class LoRA:
    @staticmethod
    def run(lora_handler: ProcessHandler, fine_tune_job_id: UUID) -> ProcessExitStatus:
        logger.info('Starting LoRA...')

        bind = f'{WORKDIR}/home:/home'
        cmd = (
            'apptainer run '
            '--nv '
            f'--bind {bind} '
            f'--env-file {ENV_PATH} '
            f'--env http_proxy={HTTP_PROXY} '
            f'--env https_proxy={HTTPS_PROXY} '
            f'--env FINE_TUNE_JOB_ID={fine_tune_job_id} '
            f'{LORA_SIF_PATH}'
        )
        process = Popen(cmd, shell=True)
        exit_status = lora_handler.wait(process)

        logger.info('LoRA finished')

        return exit_status


class FineTuneJobReaderThread(Thread):
    def __init__(
        self,
        job_queue: PriorityQueue[tuple[int, FineTuneJob]],
        status_tracker: FineTuneJobStatusTracker,
        status_tracker_resource: FineTuneJobStatusTrackerResource,
        inactive_stop_event: Event,
        wall_time_stop_event: Event,
        reader_thread_finished_event: Event,
    ):
        super().__init__(name=self.__class__.__name__)

        self._job_queue = job_queue
        self._status_tracker = status_tracker
        self._status_tracker_resource = status_tracker_resource
        self._inactive_stop_event = inactive_stop_event
        self._wall_time_stop_event = wall_time_stop_event
        self._reader_thread_finished_event = reader_thread_finished_event

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        DELAY = 60

        while True:
            if self._inactive_stop_event.is_set() or self._wall_time_stop_event.is_set():
                break

            # read batch job files
            for path in WORKDIR.glob(JOB_PATH_PATTERN):
                with path.open('r') as file:
                    json_dict = json.load(file)
                    json_dict['fine_tune_job_id'] = UUID(json_dict['fine_tune_job_id'])
                    job = FineTuneJob(**json_dict)

                self._job_queue.put((job.timestamp, job))

                # critical section
                self._status_tracker_resource.acquire()

                if self._status_tracker.is_status_update_allowed:
                    self._status_tracker.set_status(job.fine_tune_job_id, FineTuneJobStatus.WAITING)

                self._status_tracker_resource.release()
                path.unlink()

            sleep(DELAY)

        self._reader_thread_finished_event.set()
        logger.info(f'{self.__class__.__name__} exited')


class FineTuneJobProcessorThread(Thread):
    def __init__(
        self,
        job_queue: PriorityQueue[tuple[int, FineTuneJob]],
        status_tracker: FineTuneJobStatusTracker,
        status_tracker_resource: FineTuneJobStatusTrackerResource,
        inactive_stop_event: Event,
        wall_time_stop_event: Event,
        processor_thread_finished_event: Event,
    ):
        super().__init__(name=self.__class__.__name__)

        self._job_queue = job_queue
        self._status_tracker = status_tracker
        self._status_tracker_resource = status_tracker_resource
        self._inactive_stop_event = inactive_stop_event
        self._wall_time_stop_event = wall_time_stop_event
        self._processor_thread_finished_event = processor_thread_finished_event

        self._previous_job: FineTuneJob | None = None
        self._lora_handler = ProcessHandler(wall_time_stop_event)

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        DELAY = 30
        time_inactive = timedelta()

        while True:
            if self._wall_time_stop_event.is_set():
                break

            if time_inactive >= INACTIVE_THRESHOLD:
                self._inactive_stop_event.set()

                # critical section
                self._status_tracker_resource.acquire()
                self._status_tracker.is_status_update_allowed = False
                self._status_tracker_resource.release()
                break

            try:
                _, job = self._job_queue.get_nowait()
                time_inactive = timedelta()

            except Empty:
                sleep(DELAY)
                time_inactive += timedelta(seconds=DELAY)
                continue

            # critical section
            self._status_tracker_resource.acquire()
            self._status_tracker.set_status(job.fine_tune_job_id, FineTuneJobStatus.RUNNING)
            self._status_tracker_resource.release()

            # run optuna
            LoRA.run(self._lora_handler, job.fine_tune_job_id)
            self._previous_job = job

            if self._wall_time_stop_event.is_set():
                break

            # critical section
            self._status_tracker_resource.acquire()
            self._status_tracker.set_status(job.fine_tune_job_id, FineTuneJobStatus.FINISHED)
            self._status_tracker_resource.release()

        self._processor_thread_finished_event.set()
        logger.info(f'{self.__class__.__name__} exited')


class WallTimeTrackerThread(Thread):
    def __init__(
        self,
        status_tracker: FineTuneJobStatusTracker,
        status_tracker_resource: FineTuneJobStatusTrackerResource,
        inactive_stop_event: Event,
        wall_time_stop_event: Event,
        reader_thread_finished_event: Event,
        processor_thread_finished_event: Event,
    ):
        super().__init__(name=self.__class__.__name__)

        self._status_tracker = status_tracker
        self._status_tracker_resource = status_tracker_resource
        self._inactive_stop_event = inactive_stop_event
        self._wall_time_stop_event = wall_time_stop_event
        self._reader_thread_finished_event = reader_thread_finished_event
        self._processor_thread_finished_event = processor_thread_finished_event

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        DELAY = 5 * 60
        cmd = (
            f'qstat -f {PBS_JOB_ID} | '
            "awk -F'= ' "
            "'/Resource_List.walltime/ { walltime = $2 } "
            '/resources_used.walltime/ { used = $2 } '
            'END { print walltime "\\n" used }\''
        )

        while True:
            if self._inactive_stop_event.is_set():
                break

            # read wall time
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, shell=True)
            wall_times = result.stdout.strip().splitlines()

            if len(wall_times) == 1:
                sleep(DELAY)
                continue

            hours, minutes, seconds = map(int, wall_times[0].split(':'))
            wall_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            hours, minutes, seconds = map(int, wall_times[1].split(':'))
            wall_time_used = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            wall_time_left = wall_time - wall_time_used

            if wall_time_left < WALL_TIME_THRESHOLD:
                self._wall_time_stop_event.set()

                # wait for other threads to stop
                self._reader_thread_finished_event.wait()
                self._processor_thread_finished_event.wait()

                # critical section
                self._status_tracker_resource.acquire()
                self._status_tracker.is_status_update_allowed = False

                for id, status in self._status_tracker.id_to_status.items():
                    if status != FineTuneJobStatus.FINISHED:
                        self._status_tracker.set_status(id, FineTuneJobStatus.UNFINISHED)

                self._status_tracker_resource.release()
                break

            sleep(DELAY)

        logger.info(f'{self.__class__.__name__} exited')


def main():
    # multi-threaded variables
    job_queue: Queue[FineTuneJob] = Queue()
    status_tracker = FineTuneJobStatusTracker()
    status_tracker_resource = FineTuneJobStatusTrackerResource()
    inactive_stop_event = Event()
    wall_time_stop_event = Event()
    reader_thread_finished_event = Event()
    processor_thread_finished_event = Event()

    # create status file
    with STATUS_TRACKER_PATH.open('w') as file:
        json_str = status_tracker.to_json()
        file.write(json_str)
        file.flush()

    # threads
    job_reader_thread = FineTuneJobReaderThread(
        job_queue,
        status_tracker,
        status_tracker_resource,
        inactive_stop_event,
        wall_time_stop_event,
        reader_thread_finished_event,
    )
    job_processor_thread = FineTuneJobProcessorThread(
        job_queue,
        status_tracker,
        status_tracker_resource,
        inactive_stop_event,
        wall_time_stop_event,
        processor_thread_finished_event,
    )
    wall_time_tracker_thread = WallTimeTrackerThread(
        status_tracker,
        status_tracker_resource,
        inactive_stop_event,
        wall_time_stop_event,
        reader_thread_finished_event,
        processor_thread_finished_event,
    )

    job_reader_thread.start()
    job_processor_thread.start()
    wall_time_tracker_thread.start()

    job_reader_thread.join()
    job_processor_thread.join()
    wall_time_tracker_thread.join()

    logger.info('All threads have exited')


if __name__ == '__main__':
    main()
