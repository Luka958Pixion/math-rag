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

# text embeddings inference
TEI_BASE_URL = 'http://0.0.0.0:8000'
TEI_SERVER_INSTANCE_NAME = 'tei_server_instance'

# prometheus
PROMETHEUS_BASE_URL = 'http://0.0.0.0:9090'

# paths
WORKDIR = Path('.')
ENV_PATH = Path('.env.hpc.hf.tei')
CLI_SIF_PATH = Path('cli.sif')
CLIENT_SIF_PATH = Path('client.sif')
SERVER_SIF_PATH = Path('server.sif')
STATUS_TRACKER_PATH = Path(f'status_tracker_{PBS_JOB_ID}.json')
STATUS_TRACKER_TMP_PATH = STATUS_TRACKER_PATH.with_suffix('.tmp')

# path patterns
BATCH_JOB_PATH_PATTERN = f'batch_job_{PBS_JOB_ID}_*.json'

# thresholds
INACTIVE_THRESHOLD = timedelta(minutes=15)
WALL_TIME_THRESHOLD = timedelta(minutes=5)

basicConfig(
    level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
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
    def download_model(
        cli_state: ProcessHandler, model_hub_id: str
    ) -> ProcessExitStatus:
        logger.info(f'Starting {model_hub_id} download...')

        bind = f'{WORKDIR}/mount:/mount'
        cmd = (
            'apptainer run '
            '--nv '
            f'--bind {bind} '
            f'--env-file {ENV_PATH} '
            f'--env MODEL_HUB_ID={model_hub_id} '
            f'--env http_proxy={HTTP_PROXY} '
            f'--env https_proxy={HTTPS_PROXY} '
            f'{CLI_SIF_PATH}'
        )
        process = Popen(cmd, shell=True)
        exit_status = cli_state.wait(process)

        logger.info(f'Downloaded {model_hub_id}')

        return exit_status


class ServerInstance:
    @staticmethod
    def start(
        server_state: ProcessHandler, mount_path: Path, data_path: Path
    ) -> ProcessExitStatus:
        logger.info(f'Starting {TEI_SERVER_INSTANCE_NAME}...')

        bindings = [
            f'{mount_path}:/model',
            f'{data_path}:/data',
        ]
        bind = ','.join(bindings)
        cmd = (
            'apptainer instance start '
            '--nv '
            f'--bind {bind} '
            f'{SERVER_SIF_PATH} '
            f'{TEI_SERVER_INSTANCE_NAME}'
        )
        process = Popen(cmd, shell=True)
        exit_status = server_state.wait(process)

        POLL_INTERVAL = 5
        parsed_url = urlparse(TEI_BASE_URL)

        if not parsed_url.port:
            raise ValueError('TEI_BASE_URL does not include a port')

        logger.info(
            f'Waiting for {TEI_SERVER_INSTANCE_NAME} (TEI) to become healthy...'
        )

        while True:
            connection = None

            try:
                connection = HTTPConnection(parsed_url.hostname, parsed_url.port)
                connection.request('GET', '/health')
                response = connection.getresponse()

                if response.status == 200:
                    logger.info(f'{TEI_SERVER_INSTANCE_NAME} is healthy')
                    break

                else:
                    logger.info(
                        f'Health check returned status {response.status}, '
                        f'retrying in {POLL_INTERVAL}s...'
                    )

            except Exception as e:
                logger.info(
                    f'Health check failed: {e}, retrying in {POLL_INTERVAL}s...'
                )

            finally:
                if connection:
                    connection.close()

            sleep(POLL_INTERVAL)

        parsed_url = urlparse(PROMETHEUS_BASE_URL)

        if not parsed_url.port:
            raise ValueError('PROMETHEUS_BASE_URL does not include a port')

        logger.info(
            f'Waiting for {TEI_SERVER_INSTANCE_NAME} (Prometheus) to become healthy...'
        )

        while True:
            connection = None

            try:
                connection = HTTPConnection(parsed_url.hostname, parsed_url.port)
                connection.request('GET', '/-/ready')
                response = connection.getresponse()

                if response.status == 200:
                    logger.info(f'{TEI_SERVER_INSTANCE_NAME} (Prometheus) is healthy')
                    break

                else:
                    logger.info(
                        f'Health check returned status {response.status}, '
                        f'retrying in {POLL_INTERVAL}s...'
                    )

            except Exception as e:
                logger.info(
                    f'Health check failed: {e}, retrying in {POLL_INTERVAL}s...'
                )

            finally:
                if connection:
                    connection.close()

            sleep(POLL_INTERVAL)

        return exit_status

    @staticmethod
    def stop():
        # take a snapshot
        parsed_url = urlparse(PROMETHEUS_BASE_URL)

        if not parsed_url.port:
            raise ValueError('PROMETHEUS_BASE_URL does not include a port')

        connection = None

        try:
            connection = HTTPConnection(parsed_url.hostname, parsed_url.port)
            connection.request('POST', '/api/v1/admin/tsdb/snapshot')
            response = connection.getresponse()

            if response.status == 200:
                body = response.read()
                snapshot = json.loads(body)
                logger.info(f'Prometheus snapshot: {snapshot}')

                with open(f'snapshot_{PBS_JOB_ID}.json', 'w') as file:
                    json.dump(snapshot, file)

            else:
                logger.warning(f'Snapshot returned status {response.status}')
                logger.warning(f'Snapshot returned: {response.read().decode()}')

        except Exception as e:
            logger.error(f'Snapshot failed: {e}')

        finally:
            if connection:
                connection.close()

        # check targets endpoint
        connection = None

        try:
            connection = HTTPConnection(parsed_url.hostname, parsed_url.port)
            connection.request('GET', '/api/v1/targets')
            response = connection.getresponse()

            if response.status == 200:
                logger.info(f'Targets returned status {response.status}')

            else:
                logger.warning(f'Targets returned status {response.status}')
                logger.warning(f'Targets returned: {response.read().decode()}')

        except Exception as e:
            logger.error(f'Targets failed: {e}')

        finally:
            if connection:
                connection.close()

        # check metrics endpoint
        parsed_url = urlparse(TEI_BASE_URL)

        if not parsed_url.port:
            raise ValueError('TEI_BASE_URL does not include a port')

        connection = None

        try:
            connection = HTTPConnection(parsed_url.hostname, parsed_url.port)
            connection.request('GET', '/metrics')
            response = connection.getresponse()

            if response.status == 200:
                logger.info(f'Metrics returned status {response.status}')

            else:
                logger.warning(f'Metrics returned status {response.status}')
                logger.warning(f'Metrics returned: {response.read().decode()}')

        except Exception as e:
            logger.error(f'Metrics failed: {e}')

        finally:
            if connection:
                connection.close()

        cmd = f'apptainer instance stop {TEI_SERVER_INSTANCE_NAME}'
        subprocess.run(cmd, check=True, capture_output=False, shell=True)

        logger.info(f'{TEI_SERVER_INSTANCE_NAME} stopped')


class Client:
    @staticmethod
    def run(client_state: ProcessHandler, batch_request_id: UUID) -> ProcessExitStatus:
        logger.info('Starting client...')

        cmd = (
            'apptainer run '
            f'--env-file {ENV_PATH} '
            f'--env TEI_BASE_URL={TEI_BASE_URL} '
            f'--env BATCH_REQUEST_ID={batch_request_id} '
            f'{CLIENT_SIF_PATH}'
        )
        process = Popen(cmd, shell=True)
        exit_status = client_state.wait(process)

        logger.info('Client finished')

        return exit_status


class BatchJobReaderThread(Thread):
    def __init__(
        self,
        batch_job_queue: PriorityQueue[tuple[int, BatchJob]],
        status_tracker: BatchJobStatusTracker,
        status_tracker_resource: BatchJobStatusTrackerResource,
        inactive_stop_event: Event,
        wall_time_stop_event: Event,
        reader_thread_finished_event: Event,
    ):
        super().__init__(name=self.__class__.__name__)

        self._batch_job_queue = batch_job_queue
        self._status_tracker = status_tracker
        self._status_tracker_resource = status_tracker_resource
        self._inactive_stop_event = inactive_stop_event
        self._wall_time_stop_event = wall_time_stop_event
        self._reader_thread_finished_event = reader_thread_finished_event

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        DELAY = 60

        while True:
            if (
                self._inactive_stop_event.is_set()
                or self._wall_time_stop_event.is_set()
            ):
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
        status_tracker: BatchJobStatusTracker,
        status_tracker_resource: BatchJobStatusTrackerResource,
        inactive_stop_event: Event,
        wall_time_stop_event: Event,
        processor_thread_finished_event: Event,
    ):
        super().__init__(name=self.__class__.__name__)

        self._batch_job_queue = batch_job_queue
        self._status_tracker = status_tracker
        self._status_tracker_resource = status_tracker_resource
        self._inactive_stop_event = inactive_stop_event
        self._wall_time_stop_event = wall_time_stop_event
        self._processor_thread_finished_event = processor_thread_finished_event

        self._previous_batch_job: BatchJob | None = None
        self._cli_handler = ProcessHandler(wall_time_stop_event)
        self._client_handler = ProcessHandler(wall_time_stop_event)
        self._server_handler = ProcessHandler(wall_time_stop_event)

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        DELAY = 30
        time_inactive = timedelta()
        is_server_instance_running = False

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
            data_path = WORKDIR / 'data'

            if not mount_path.exists():
                mount_path.mkdir(parents=True)
                HuggingFaceCLI.download_model(self._cli_handler, batch_job.model_hub_id)

                if self._wall_time_stop_event.is_set():
                    break

            if not self._previous_batch_job:
                # start server instance
                server_instance_exit_status = ServerInstance.start(
                    self._server_handler, mount_path, data_path
                )

                if server_instance_exit_status == ProcessExitStatus.COMPLETED:
                    is_server_instance_running = True

                if self._wall_time_stop_event.is_set():
                    break

            # restart instances with another model
            elif self._previous_batch_job.model_hub_id != batch_job.model_hub_id:
                ServerInstance.stop()
                server_instance_exit_status = ServerInstance.start(
                    self._server_handler, mount_path, data_path
                )

                if server_instance_exit_status == ProcessExitStatus.COMPLETED:
                    is_server_instance_running = True

                if self._wall_time_stop_event.is_set():
                    break

            # run client
            Client.run(self._client_handler, batch_job.batch_request_id)
            self._previous_batch_job = batch_job

            if self._wall_time_stop_event.is_set():
                break

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


class WallTimeTrackerThread(Thread):
    def __init__(
        self,
        status_tracker: BatchJobStatusTracker,
        status_tracker_resource: BatchJobStatusTrackerResource,
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
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, shell=True
            )
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
                    if status != BatchJobStatus.FINISHED:
                        self._status_tracker.set_status(id, BatchJobStatus.UNFINISHED)

                self._status_tracker_resource.release()
                break

            sleep(DELAY)

        logger.info(f'{self.__class__.__name__} exited')


def main():
    # multi-threaded variables
    batch_job_queue: Queue[BatchJob] = Queue()
    status_tracker = BatchJobStatusTracker()
    status_tracker_resource = BatchJobStatusTrackerResource()
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
    batch_job_reader_thread = BatchJobReaderThread(
        batch_job_queue,
        status_tracker,
        status_tracker_resource,
        inactive_stop_event,
        wall_time_stop_event,
        reader_thread_finished_event,
    )
    batch_job_processor_thread = BatchJobProcessorThread(
        batch_job_queue,
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

    batch_job_reader_thread.start()
    batch_job_processor_thread.start()
    wall_time_tracker_thread.start()

    batch_job_reader_thread.join()
    batch_job_processor_thread.join()
    wall_time_tracker_thread.join()

    logger.info('All threads have exited')


if __name__ == '__main__':
    main()
