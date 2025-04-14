import json
import os
import subprocess

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from http.client import HTTPConnection
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from queue import Empty, PriorityQueue
from threading import Event, Thread
from time import sleep
from urllib.parse import urlparse
from uuid import UUID


PBS_JOB_ID = os.environ['PBS_JOBID']

HTTP_PROXY = 'http://10.150.1.1:3128'
HTTPS_PROXY = 'http://10.150.1.1:3128'

TGI_BASE_URL = 'http://0.0.0.0:8000'

WORKDIR = Path('.')
STATUS_PATH = Path('status.json')
STATUS_TMP_PATH = STATUS_PATH.with_suffix('.tmp')
BATCH_JOB_PATH_PATTERN = 'batch_job_*.json'

INACTIVE_THRESHOLD = timedelta(minutes=15)

basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


@dataclass
class BatchJob:
    batch_request_id: UUID
    model_hub_id: str
    timestamp: int


class BatchJobStatus(str, Enum):
    WAITING = 'waiting'
    RUNNING = 'running'
    FINISHED = 'finished'
    # FAILED = 'failed'


class BatchJobStatusTracker:
    def __init__(self):
        self._statuses: dict[UUID, BatchJobStatus] = {}

    def get_status(self, batch_id: UUID) -> BatchJobStatus | None:
        return self._statuses.get(batch_id)

    def set_status(self, batch_id: UUID, status: BatchJobStatus):
        self._statuses[batch_id] = status
        self._atomic_write_statuses()

    def clear(self):
        self._statuses = {}
        self._atomic_write_statuses()

    def _atomic_write_statuses(self):
        with STATUS_TMP_PATH.open('w') as file:
            statuses_json_dict = {
                str(key): str(value.value) for key, value in self._statuses.items()
            }
            json.dump(statuses_json_dict, file)
            file.flush()
            os.fsync(file.fileno())

        os.replace(STATUS_TMP_PATH, STATUS_PATH)


class HuggingFaceCLI:
    @staticmethod
    def download_model(model_hub_id: str):
        env = os.environ.copy()
        env['http_proxy'] = HTTP_PROXY
        env['https_proxy'] = HTTPS_PROXY

        bind = f'{WORKDIR}/mount:/mount'
        cmd = f'apptainer run --nv --bind {bind} --env MODEL_HUB_ID={model_hub_id} cli.sif'
        subprocess.run(cmd, check=True, capture_output=False, shell=True, env=env)


class TGIServerInstance:
    @staticmethod
    def start(mount_path: Path):
        logger.info('Starting TGI server...')

        bind = f'{mount_path}:/model'
        cmd = f'apptainer instance start --nv --bind {bind} server.sif tgi_server_instance'
        subprocess.run(cmd, check=True, capture_output=False, shell=True)

        POLL_INTERVAL = 5
        parsed_url = urlparse(TGI_BASE_URL)

        if not parsed_url.port:
            raise ValueError('TGI_BASE_URL does not include a port')

        client = HTTPConnection(parsed_url.hostname, parsed_url.port, timeout=3)
        logger.info('Waiting for TGI server to become healthy...')

        while True:
            try:
                client.request('GET', '/health')
                response = client.getresponse()

                if response.status == 200:
                    logger.info('TGI server is healthy.')
                    break

                else:
                    logger.info(
                        f'Health check returned status {response.status}. '
                        f'Retrying in {POLL_INTERVAL}s...'
                    )

            except Exception as e:
                logger.info(
                    f'Health check failed: {e}. Retrying in {POLL_INTERVAL}s...'
                )

            sleep(POLL_INTERVAL)

    @staticmethod
    def stop():
        cmd = f'apptainer instance stop tgi_server_instance'
        subprocess.run(cmd, check=True, capture_output=False, shell=True)


class TGIClient:
    @staticmethod
    def run(batch_request_id: UUID):
        env = os.environ.copy()
        env['TGI_BASE_URL'] = TGI_BASE_URL
        env['BATCH_REQUEST_ID'] = batch_request_id

        cmd = 'apptainer run --env-file .env.hpc.hf.tgi client.sif'
        subprocess.run(cmd, check=True, capture_output=False, shell=True, env=env)


def read_batch_job_file(
    batch_job_queue: PriorityQueue[tuple[int, BatchJob]],
    batch_job_status_tracker: BatchJobStatusTracker,
    stop_event: Event,
):
    while True:
        if stop_event.is_set():
            break

        # read batch job files
        batch_job_file_paths = WORKDIR.glob(BATCH_JOB_PATH_PATTERN)

        for batch_job_file_path in batch_job_file_paths:
            with batch_job_file_path.open('r') as file:
                data = json.load(file)
                data['batch_request_id'] = UUID(data['batch_request_id'])
                batch_job = BatchJob(**data)
                batch_job_queue.put((batch_job.timestamp, batch_job))

                batch_job_status_tracker.set_status(
                    batch_job.batch_request_id, BatchJobStatus.WAITING
                )

            # delete batch job files after reading
            batch_job_file_path.unlink()

        sleep(60)


def process_batch_request(
    batch_job_queue: PriorityQueue[tuple[int, BatchJob]],
    previous_batch_job: BatchJob | None,
    batch_job_status_tracker: BatchJobStatusTracker,
    stop_event: Event,
):
    DELAY = 30
    time_inactive = timedelta()
    is_server_instance_running = False

    while True:
        if time_inactive >= INACTIVE_THRESHOLD:
            batch_job_status_tracker.clear()
            stop_event.set()
            break

        try:
            _, batch_job = batch_job_queue.get_nowait()
            time_inactive = timedelta()

        except Empty:
            sleep(DELAY)
            time_inactive += timedelta(seconds=DELAY)
            continue

        batch_job_status_tracker.set_status(
            batch_job.batch_request_id, BatchJobStatus.RUNNING
        )
        mount_path = WORKDIR / 'mount' / batch_job.model_hub_id

        if not mount_path.exists():
            mount_path.mkdir(parents=True)
            HuggingFaceCLI.download_model(batch_job.model_hub_id)

        if not previous_batch_job:
            TGIServerInstance.start(mount_path)
            is_server_instance_running = True

        elif previous_batch_job.model_hub_id != batch_job.model_hub_id:
            TGIServerInstance.stop()
            TGIServerInstance.start(mount_path)
            is_server_instance_running = True

        TGIClient.run(batch_job.batch_request_id)
        previous_batch_job = batch_job
        batch_job_status_tracker.set_status(
            batch_job.batch_request_id, BatchJobStatus.FINISHED
        )

    if is_server_instance_running:
        TGIServerInstance.stop()


def main():
    batch_job_queue: PriorityQueue[tuple[int, BatchJob]] = PriorityQueue()
    previous_batch_job: BatchJob | None = None
    batch_job_status_tracker = BatchJobStatusTracker()
    stop_event = Event()

    batch_job_reader_thread = Thread(
        target=read_batch_job_file,
        args=(
            batch_job_queue,
            batch_job_status_tracker,
            stop_event,
        ),
        name='BatchJobReaderThread',
    )
    batch_request_processor_thread = Thread(
        target=process_batch_request,
        args=(
            batch_job_queue,
            previous_batch_job,
            batch_job_status_tracker,
            stop_event,
        ),
        name='BatchRequestProcessorThread',
    )

    batch_job_reader_thread.start()
    batch_request_processor_thread.start()

    batch_job_reader_thread.join()
    batch_request_processor_thread.join()


if __name__ == '__main__':
    main()
