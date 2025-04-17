import json
import os
import subprocess

from dataclasses import asdict, dataclass
from datetime import timedelta
from enum import Enum
from http.client import HTTPConnection
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from queue import Empty, PriorityQueue, Queue
from subprocess import Popen, TimeoutExpired
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
BATCH_JOB_PATH_PATTERN = 'batch_job_{PBS_JOB_ID}_*.json'

# thresholds
INACTIVE_THRESHOLD = timedelta(minutes=15)
WALLTIME_THRESHOLD = timedelta(minutes=5)
INITIALIZE_THRESHOLD = timedelta(minutes=10)

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

        self._process.wait()

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
        self.waiting = Queue()
        self.lock = Lock()
        self.condition = Condition()

    def acquire(self):
        turn = object()

        with self.condition:
            self.waiting.put(turn)

            while self.waiting.queue[0] is not turn:
                self.condition.wait()

            self.lock.acquire()

    def release(self):
        with self.condition:
            self.lock.release()
            self.waiting.get()
            self.condition.notify_all()


class BatchJobStatusTracker:
    def __init__(self):
        self._is_status_update_allowed = True
        self._id_to_status: dict[UUID, BatchJobStatus] = {}

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
            json_dict = self.to_json()
            json.dump(json_dict, file)
            file.flush()
            os.fsync(file.fileno())

        os.replace(STATUS_TRACKER_TMP_PATH, STATUS_TRACKER_PATH)

    def to_json(self) -> str:
        def encoder(obj):
            if isinstance(obj, UUID):
                return str(obj)

            if isinstance(obj, Enum):
                return obj.value

            raise TypeError(f'Type {type(obj)} not serializable')

        return json.dumps(asdict(self), default=encoder)

    @staticmethod
    def from_json(data: str) -> 'BatchJobStatusTracker':
        json_dict = json.loads(data)

        return BatchJobStatusTracker(
            is_status_update_allowed=json_dict['pbs_job_running'],
            id_to_status={
                UUID(key): BatchJobStatus(value)
                for key, value in cast(dict, json_dict['statuses']).items()
            },
        )


class HuggingFaceCLI:
    @staticmethod
    def download_model(cli_state: ProcessState, model_hub_id: str):
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
        process = Popen(cmd, check=True, capture_output=False, shell=True, env=env)
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
        process = Popen(cmd, check=True, capture_output=False, shell=True)
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
        env = os.environ.copy()
        env['TGI_BASE_URL'] = TGI_BASE_URL
        env['BATCH_REQUEST_ID'] = str(batch_request_id)

        cmd = 'apptainer run ' f'--env-file {ENV_PATH} ' f'{CLIENT_SIF_PATH}'
        process = Popen(cmd, check=True, capture_output=False, shell=True, env=env)
        client_state.wait_process(process)


def read_batch_job(
    batch_job_queue: PriorityQueue[tuple[int, BatchJob]],
    status_tracker: BatchJobStatusTracker,
    status_tracker_resource: BatchJobStatusTrackerResource,
    inactive_stop_event: Event,
    walltime_stop_event: Event,
    reader_thread_finished_event: Event,
):
    DELAY = 60

    while True:
        if inactive_stop_event.is_set() or walltime_stop_event.is_set():
            break

        # read batch job files
        for path in WORKDIR.glob(BATCH_JOB_PATH_PATTERN):
            with path.open('r') as file:
                json_dict = json.load(file)
                json_dict['batch_request_id'] = UUID(json_dict['batch_request_id'])
                batch_job = BatchJob(**json_dict)

            # critical section
            status_tracker_resource.acquire()

            if status_tracker.is_status_update_allowed:
                batch_job_queue.put((batch_job.timestamp, batch_job))
                status_tracker.set_status(
                    batch_job.batch_request_id, BatchJobStatus.WAITING
                )
                path.unlink()

            status_tracker_resource.release()

        sleep(DELAY)

    reader_thread_finished_event.set()


def process_batch_job(
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
    DELAY = 30
    time_inactive = timedelta()
    is_server_instance_running = False

    while True:
        if walltime_stop_event.is_set():
            break

        if time_inactive >= INACTIVE_THRESHOLD:
            inactive_stop_event.set()

            # critical section
            status_tracker_resource.acquire()
            status_tracker.is_status_update_allowed = False
            status_tracker_resource.release()
            break

        try:
            _, batch_job = batch_job_queue.get_nowait()
            time_inactive = timedelta()

        except Empty:
            sleep(DELAY)
            time_inactive += timedelta(seconds=DELAY)
            continue

        # critical section
        status_tracker_resource.acquire()
        status_tracker.set_status(batch_job.batch_request_id, BatchJobStatus.RUNNING)
        status_tracker_resource.release()

        # download model if it's not downloaded already
        mount_path = WORKDIR / 'mount' / batch_job.model_hub_id

        if not mount_path.exists():
            mount_path.mkdir(parents=True)
            HuggingFaceCLI.download_model(cli_state, batch_job.model_hub_id)

        # start server instance
        if not previous_batch_job:
            ServerInstance.start(server_state, mount_path)
            is_server_instance_running = True

        # restart server instance with another model
        elif previous_batch_job.model_hub_id != batch_job.model_hub_id:
            ServerInstance.stop()
            ServerInstance.start(mount_path)
            is_server_instance_running = True

        # run client
        Client.run(client_state, batch_job.batch_request_id)
        previous_batch_job = batch_job

        # critical section
        status_tracker_resource.acquire()
        status_tracker.set_status(batch_job.batch_request_id, BatchJobStatus.FINISHED)
        status_tracker_resource.release()

    if is_server_instance_running:
        ServerInstance.stop()

    processor_thread_finished_event.set()


def track_walltime(
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
    DELAY = 5 * 60
    cmd = (
        f'qstat -f {PBS_JOB_ID} | '
        "awk -F'= ' "
        "'/Resource_List.walltime|resources_used.walltime/ { print $2 }'"
    )

    while True:
        if inactive_stop_event.is_set():
            break

        # read walltime
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, shell=True
        )
        walltimes = result.stdout.strip().splitlines()
        walltime = timedelta(walltimes[0])
        walltime_used = timedelta(walltimes[1])
        walltime_left = walltime - walltime_used

        if walltime_left < WALLTIME_THRESHOLD:
            walltime_stop_event.set()

            # stop long running processes
            for state in (cli_state, client_state, server_state):
                state.stop_process()

            # wait for other threads to stop
            reader_thread_finished_event.wait()
            processor_thread_finished_event.wait()

            # critical section
            status_tracker_resource.acquire()
            status_tracker.is_status_update_allowed = False

            for id, status in status_tracker.id_to_status.items():
                if status != BatchJobStatus.FINISHED:
                    status_tracker.set_status(id, BatchJobStatus.UNFINISHED)

            status_tracker_resource.release()
            break

        sleep(DELAY)


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
        json_dict = status_tracker.to_json()
        json.dump(json_dict, file)
        file.flush()

    # threads
    batch_job_reader_thread = Thread(
        target=read_batch_job,
        args=(
            batch_job_queue,
            status_tracker,
            status_tracker_resource,
            inactive_stop_event,
            walltime_stop_event,
            reader_thread_finished_event,
        ),
        name='BatchJobReaderThread',
    )
    batch_job_processor_thread = Thread(
        target=process_batch_job,
        args=(
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
        ),
        name='BatchJobProcessorThread',
    )
    walltime_tracker_thread = Thread(
        target=track_walltime,
        args=(
            status_tracker,
            status_tracker_resource,
            inactive_stop_event,
            walltime_stop_event,
            reader_thread_finished_event,
            processor_thread_finished_event,
            cli_state,
            client_state,
            server_state,
        ),
        name='WalltimeTrackerThread',
    )

    batch_job_reader_thread.start()
    batch_job_processor_thread.start()
    walltime_tracker_thread.start()

    batch_job_reader_thread.join()
    batch_job_processor_thread.join()
    walltime_tracker_thread.join()


if __name__ == '__main__':
    main()
