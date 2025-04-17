import json
import os
import subprocess

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from http.client import HTTPConnection
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from queue import Empty, PriorityQueue, Queue
from subprocess import CalledProcessError, Popen, TimeoutExpired
from threading import Condition, Event, Lock, Thread
from time import sleep
from typing import cast
from urllib.parse import urlparse
from uuid import UUID


# current job
PBS_JOB_ID = os.environ['PBS_JOBID']

# squid proxy
HTTP_PROXY = 'http://10.150.1.1:3128'
HTTPS_PROXY = 'http://10.150.1.1:3128'

# text generation inference
TGI_BASE_URL = 'http://0.0.0.0:8000'
TGI_SERVER_INSTANCE_NAME = 'tgi_server_instance'

# paths
WORKDIR = Path('.')
ENV_PATH = Path('.env.hpc.hf.tgi')
CLI_SIF_PATH = Path('cli.sif')
CLIENT_SIF_PATH = Path('client.sif')
SERVER_SIF_PATH = Path('server.sif')
STATUS_TRACKER_PATH = Path(f'status_tracker_{PBS_JOB_ID}.json')
STATUS_TRACKER_TMP_PATH = STATUS_TRACKER_PATH.with_suffix('.tmp')

# path patterns
BATCH_JOB_PATH_PATTERN = f'batch_job_{PBS_JOB_ID}_*.json'

# thresholds
INACTIVE_THRESHOLD = timedelta(minutes=10)  # TODO, move to 15
WALLTIME_THRESHOLD = timedelta(minutes=5)

basicConfig(
    level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
logger = getLogger(__name__)


class ProcessState:
    def __init__(self):
        self._lock: Lock = Lock()
        self._process: Popen | None = None

    def wait_process(self, process: Popen):
        with self._lock:
            self._process = process

        return_code = self._process.wait()

        if return_code != 0:
            raise CalledProcessError(return_code, self._process.args)

    def stop_process(self):
        with self._lock:
            process = self._process

        if process and process.poll() is None:
            process.terminate()

            try:
                process.wait(timeout=5)

            except TimeoutExpired:
                process.kill()


@dataclass
class BatchJob:
    batch_request_id: UUID
    model_hub_id: str
    timestamp: int


class BatchJobStatus(str, Enum):
    WAITING = 'waiting'
    RUNNING = 'running'
    FINISHED = 'finished'
    UNFINISHED = 'unfinished'


class BatchJobStatusTrackerResource:
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


class BatchJobStatusTracker:
    def __init__(
        self,
        is_status_update_allowed: bool = True,
        id_to_status: dict[UUID, BatchJobStatus] | None = None,
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
    def id_to_status(self) -> dict[UUID, BatchJobStatus]:
        return self._id_to_status

    def get_status(self, batch_id: UUID) -> BatchJobStatus | None:
        return self._id_to_status.get(batch_id)

    def set_status(self, batch_id: UUID, status: BatchJobStatus):
        if self._is_status_update_allowed:
            self._id_to_status[batch_id] = status
            self._atomic_write()

    def _atomic_write(self):
        with STATUS_TRACKER_TMP_PATH.open('w') as file:
            json_str = self.to_json()
            file.write(json_str)
            file.flush()
            os.fsync(file.fileno())

        os.replace(STATUS_TRACKER_TMP_PATH, STATUS_TRACKER_PATH)

    def to_json(self) -> str:
        json_dict = {
            'is_status_update_allowed': self._is_status_update_allowed,
            'id_to_status': {
                str(key): value.value for key, value in self._id_to_status.items()
            },
        }

        return json.dumps(json_dict)

    @staticmethod
    def from_json(json_str: str) -> 'BatchJobStatusTracker':
        json_dict = json.loads(json_str)

        return BatchJobStatusTracker(
            is_status_update_allowed=json_dict['is_status_update_allowed'],
            id_to_status={
                UUID(key): BatchJobStatus(value)
                for key, value in cast(dict, json_dict['id_to_status']).items()
            },
        )


class HuggingFaceCLI:
    @staticmethod
    def download_model(cli_state: ProcessState, model_hub_id: str):
        logger.info(f'Starting {model_hub_id} download...')

        env = os.environ.copy()
        env['http_proxy'] = HTTP_PROXY
        env['https_proxy'] = HTTPS_PROXY

        bind = f'{WORKDIR}/mount:/mount'
        cmd = (
            'apptainer run '
            '--nv '
            f'--bind {bind} '
            f'--env-file {ENV_PATH} '
            f'--env MODEL_HUB_ID={model_hub_id} '
            f'{CLIENT_SIF_PATH}'
        )
        process = Popen(cmd, shell=True, env=env)
        cli_state.wait_process(process)


class ServerInstance:
    @staticmethod
    def start(server_state: ProcessState, mount_path: Path):
        logger.info(f'Starting {TGI_SERVER_INSTANCE_NAME}...')

        bind = f'{mount_path}:/model'
        cmd = (
            'apptainer instance start '
            '--nv '
            f'--bind {bind} '
            f'{SERVER_SIF_PATH} '
            f'{TGI_SERVER_INSTANCE_NAME}'
        )
        process = Popen(cmd, shell=True)
        server_state.wait_process(process)

        POLL_INTERVAL = 5
        parsed_url = urlparse(TGI_BASE_URL)

        if not parsed_url.port:
            raise ValueError('TGI_BASE_URL does not include a port')

        logger.info(f'Waiting for {TGI_SERVER_INSTANCE_NAME} to become healthy...')

        while True:
            try:
                connection = HTTPConnection(parsed_url.hostname, parsed_url.port)
                connection.request('GET', '/health')
                response = connection.getresponse()

                if response.status == 200:
                    logger.info(f'{TGI_SERVER_INSTANCE_NAME} is healthy')
                    break

                else:
                    logger.info(
                        f'Health check returned status {response.status}, '
                        f'retrying in {POLL_INTERVAL}s...'
                    )

            except Exception as e:
                logger.info(
                    f'Health check failed: {e}, ' f'retrying in {POLL_INTERVAL}s...'
                )

            sleep(POLL_INTERVAL)

    @staticmethod
    def stop():
        cmd = f'apptainer instance stop {TGI_SERVER_INSTANCE_NAME}'
        subprocess.run(cmd, check=True, capture_output=False, shell=True)


class Client:
    @staticmethod
    def run(client_state: ProcessState, batch_request_id: UUID):
        logger.info('Starting client...')

        env = os.environ.copy()
        env['TGI_BASE_URL'] = TGI_BASE_URL
        env['BATCH_REQUEST_ID'] = str(batch_request_id)

        cmd = 'apptainer run ' f'--env-file {ENV_PATH} ' f'{CLIENT_SIF_PATH}'
        process = Popen(cmd, shell=True, env=env)
        client_state.wait_process(process)


class BatchJobReaderThread(Thread):
    def __init__(
        self,
        batch_job_queue: PriorityQueue[tuple[int, BatchJob]],
        status_tracker: BatchJobStatusTracker,
        status_tracker_resource: BatchJobStatusTrackerResource,
        inactive_stop_event: Event,
        walltime_stop_event: Event,
        reader_thread_finished_event: Event,
    ):
        super().__init__(name=self.__class__.__name__)

        self._batch_job_queue = batch_job_queue
        self._status_tracker = status_tracker
        self._status_tracker_resource = status_tracker_resource
        self._inactive_stop_event = inactive_stop_event
        self._walltime_stop_event = walltime_stop_event
        self._reader_thread_finished_event = reader_thread_finished_event

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        DELAY = 60

        while True:
            if self._inactive_stop_event.is_set() or self._walltime_stop_event.is_set():
                break

            # read batch job files
            for path in WORKDIR.glob(BATCH_JOB_PATH_PATTERN):
                with path.open('r') as file:
                    json_dict = json.load(file)
                    json_dict['batch_request_id'] = UUID(json_dict['batch_request_id'])
                    batch_job = BatchJob(**json_dict)

                self._batch_job_queue.put((batch_job.timestamp, batch_job))

                # critical section
                self._status_tracker_resource.acquire()

                if self._status_tracker.is_status_update_allowed:
                    self._status_tracker.set_status(
                        batch_job.batch_request_id, BatchJobStatus.WAITING
                    )

                self._status_tracker_resource.release()
                path.unlink()

            sleep(DELAY)

        self._reader_thread_finished_event.set()
        logger.info(f'{self.__class__.__name__} exited')


class BatchJobProcessorThread(Thread):
    def __init__(
        self,
        batch_job_queue: PriorityQueue[tuple[int, BatchJob]],
        previous_batch_job: BatchJob | None,
        status_tracker: BatchJobStatusTracker,
        status_tracker_resource: BatchJobStatusTrackerResource,
        inactive_stop_event: Event,
        walltime_stop_event: Event,
        processor_thread_finished_event: Event,
        cli_state: ProcessState,
        client_state: ProcessState,
        server_state: ProcessState,
    ):
        super().__init__(name=self.__class__.__name__)

        self._batch_job_queue = batch_job_queue
        self._previous_batch_job = previous_batch_job
        self._status_tracker = status_tracker
        self._status_tracker_resource = status_tracker_resource
        self._inactive_stop_event = inactive_stop_event
        self._walltime_stop_event = walltime_stop_event
        self._processor_thread_finished_event = processor_thread_finished_event
        self._cli_state = cli_state
        self._client_state = client_state
        self._server_state = server_state

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        DELAY = 30
        time_inactive = timedelta()
        is_server_instance_running = False

        while True:
            if self._walltime_stop_event.is_set():
                break

            if time_inactive >= INACTIVE_THRESHOLD:
                self._inactive_stop_event.set()

                # critical section
                self._status_tracker_resource.acquire()
                self._status_tracker.is_status_update_allowed = False
                self._status_tracker_resource.release()
                break

            try:
                _, batch_job = self._batch_job_queue.get_nowait()
                time_inactive = timedelta()

            except Empty:
                sleep(DELAY)
                time_inactive += timedelta(seconds=DELAY)
                continue

            # critical section
            self._status_tracker_resource.acquire()
            self._status_tracker.set_status(
                batch_job.batch_request_id, BatchJobStatus.RUNNING
            )
            self._status_tracker_resource.release()

            # download model if it's not downloaded already
            mount_path = WORKDIR / 'mount' / batch_job.model_hub_id

            if not mount_path.exists():
                mount_path.mkdir(parents=True)
                HuggingFaceCLI.download_model(self._cli_state, batch_job.model_hub_id)

            # start server instance
            if not self._previous_batch_job:
                ServerInstance.start(self._server_state, mount_path)
                is_server_instance_running = True

            # restart server instance with another model
            elif self._previous_batch_job.model_hub_id != batch_job.model_hub_id:
                ServerInstance.stop()
                ServerInstance.start(mount_path)
                is_server_instance_running = True

            # run client
            Client.run(self._client_state, batch_job.batch_request_id)
            self._previous_batch_job = batch_job

            # critical section
            self._status_tracker_resource.acquire()
            self._status_tracker.set_status(
                batch_job.batch_request_id, BatchJobStatus.FINISHED
            )
            self._status_tracker_resource.release()

        if is_server_instance_running:
            ServerInstance.stop()

        self._processor_thread_finished_event.set()
        logger.info(f'{self.__class__.__name__} exited')


class WalltimeTrackerThread(Thread):
    def __init__(
        self,
        status_tracker: BatchJobStatusTracker,
        status_tracker_resource: BatchJobStatusTrackerResource,
        inactive_stop_event: Event,
        walltime_stop_event: Event,
        reader_thread_finished_event: Event,
        processor_thread_finished_event: Event,
        cli_state: ProcessState,
        client_state: ProcessState,
        server_state: ProcessState,
    ):
        super().__init__(name=self.__class__.__name__)

        self._status_tracker = status_tracker
        self._status_tracker_resource = status_tracker_resource
        self._inactive_stop_event = inactive_stop_event
        self._walltime_stop_event = walltime_stop_event
        self._reader_thread_finished_event = reader_thread_finished_event
        self._processor_thread_finished_event = processor_thread_finished_event
        self._cli_state = cli_state
        self._client_state = client_state
        self._server_state = server_state

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

            # read walltime
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, shell=True
            )
            walltimes = result.stdout.strip().splitlines()

            if len(walltimes) == 1:
                sleep(DELAY)
                continue

            hours, minutes, seconds = map(int, walltimes[0].split(':'))
            walltime = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            hours, minutes, seconds = map(int, walltimes[1].split(':'))
            walltime_used = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            walltime_left = walltime - walltime_used

            if walltime_left < WALLTIME_THRESHOLD:
                self._walltime_stop_event.set()

                # stop long running processes
                for state in (self._cli_state, self._client_state, self._server_state):
                    state.stop_process()

                # wait for other threads to stop
                self._reader_thread_finished_event.wait()
                self._processor_thread_finished_event.wait()

                # critical section
                self._status_tracker_resource.acquire()
                self._status_tracker.is_status_update_allowed = False

                for id, status in self._status_tracker.id_to_status.items():
                    if status != BatchJobStatus.FINISHED:
                        self._status_tracker.set_status(id, BatchJobStatus.UNFINISHED)

                self._status_tracker_resource.release()
                break

            sleep(DELAY)

        logger.info(f'{self.__class__.__name__} exited')


def main():
    # initialization
    batch_job_queue: Queue[BatchJob] = Queue()
    previous_batch_job: BatchJob | None = None
    status_tracker = BatchJobStatusTracker()
    status_tracker_resource = BatchJobStatusTrackerResource()
    inactive_stop_event = Event()
    walltime_stop_event = Event()
    reader_thread_finished_event = Event()
    processor_thread_finished_event = Event()
    cli_state = ProcessState()
    client_state = ProcessState()
    server_state = ProcessState()

    # create status file
    with STATUS_TRACKER_PATH.open('w') as file:
        json_str = status_tracker.to_json()
        file.write(json_str)
        file.flush()

    # threads
    batch_job_reader_thread = BatchJobReaderThread(
        batch_job_queue,
        status_tracker,
        status_tracker_resource,
        inactive_stop_event,
        walltime_stop_event,
        reader_thread_finished_event,
    )
    batch_job_processor_thread = BatchJobProcessorThread(
        batch_job_queue,
        previous_batch_job,
        status_tracker,
        status_tracker_resource,
        inactive_stop_event,
        walltime_stop_event,
        processor_thread_finished_event,
        cli_state,
        client_state,
        server_state,
    )
    walltime_tracker_thread = WalltimeTrackerThread(
        status_tracker,
        status_tracker_resource,
        inactive_stop_event,
        walltime_stop_event,
        reader_thread_finished_event,
        processor_thread_finished_event,
        cli_state,
        client_state,
        server_state,
    )

    batch_job_reader_thread.start()
    batch_job_processor_thread.start()
    walltime_tracker_thread.start()

    batch_job_reader_thread.join()
    batch_job_processor_thread.join()
    walltime_tracker_thread.join()

    logger.info('All threads have exited')


if __name__ == '__main__':
    main()
