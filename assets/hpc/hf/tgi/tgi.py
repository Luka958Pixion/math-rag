import json
import os
import subprocess

from datetime import timedelta
from enum import Enum
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from queue import PriorityQueue
from threading import Thread
from time import sleep
from uuid import UUID

from decouple import config
from httpx import Client
from pydantic import BaseModel


PBS_JOB_ID = config('PBS_JOBID')

WORKDIR = Path('.')

HTTP_PROXY = 'http://10.150.1.1:3128'
HTTPS_PROXY = 'http://10.150.1.1:3128'

TGI_BASE_URL = 'http://0.0.0.0:8000'
TGI_STATUS_PATH = Path('status.json')
TGI_STATUS_TMP_PATH = TGI_STATUS_PATH.with_suffix('.tmp')

WALLTIME_THRESHOLD = timedelta(minutes=10)

basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


class TGIMetadata(BaseModel):
    batch_id: UUID
    model_hub_id: str


class TGIBatchJobStatus(str, Enum):
    READY = 'ready'
    PENDING = 'pending'
    RUNNING = 'running'
    FINISHED = 'finished'
    FAILED = 'failed'


class TGIBatchJobStatusTracker:
    def __init__(self):
        self._statuses: dict[str, TGIBatchJobStatus] = {}

    def set_status(self, task_id: str, status: TGIBatchJobStatus):
        self._statuses[task_id] = status

        # atomic writing
        with TGI_STATUS_TMP_PATH.open('w') as file:
            json.dump({'status': status.value}, file)
            file.flush()
            os.fsync(file.fileno())

        os.replace(TGI_STATUS_TMP_PATH, TGI_STATUS_PATH)

    def get_status(self, task_id: str) -> TGIBatchJobStatus | None:
        return self._statuses.get(task_id)

    def remove_status(self, task_id: str):
        if task_id in self._statuses:
            del self._statuses[task_id]


class TGIStatus(BaseModel):
    pass


class Metadata(BaseModel):
    batch_request_id: UUID
    model_hub_id: str
    timestamp: int


class HuggingFaceCLI:
    @staticmethod
    def download_model(model_hub_id: str):
        env = os.environ.copy()
        env['http_proxy'] = HTTP_PROXY
        env['https_proxy'] = HTTPS_PROXY

        bind = f'{WORKDIR}/data:/data'
        cmd = f'apptainer run --nv --bind {bind} --env MODEL_HUB_ID={model_hub_id} hf_cli.sif'
        subprocess.run(cmd, check=True, capture_output=False, shell=True, env=env)


class TGIServerInstance:
    @staticmethod
    def start(mount_path: Path):
        logger.info('Starting TGI server...')

        bind = f'{mount_path}:/model'
        cmd = f'apptainer instance start --nv --bind {bind} server.sif tgi_server_instance'
        subprocess.run(cmd, check=True, capture_output=False, shell=True)

        logger.info('Waiting for TGI server to become healthy...')
        client = Client()
        poll_interval = 5

        while True:
            response = client.get(TGI_BASE_URL + '/health', timeout=3)

            if response.status_code == 200:
                logger.info('TGI server is healthy.')
                break

            logger.info(
                f'Health check returned status {response.status_code}. '
                f'Retrying in {poll_interval}s...'
            )
            sleep(poll_interval)

    @staticmethod
    def stop():
        cmd = f'apptainer instance stop tgi_server_instance'
        subprocess.run(cmd, check=True, capture_output=False, shell=True)


class TGIClient:
    @staticmethod
    def run():
        env = os.environ.copy()
        env['TGI_BASE_URL'] = TGI_BASE_URL

        cmd = 'apptainer run --env-file .env.hpc.hf.tgi client.sif'
        subprocess.run(cmd, check=True, capture_output=False, shell=True, env=env)


def watch_walltime():
    cmd = (
        f'qstat -f {PBS_JOB_ID} | '
        "awk -F'= ' "
        "'/Resource_List.walltime|resources_used.walltime/ { print $2 }'"
    )
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, shell=True)

    walltimes = result.stdout.strip().splitlines()
    walltime = timedelta(walltimes[0])
    walltime_used = timedelta(walltimes[1])

    if walltime - walltime_used < WALLTIME_THRESHOLD:
        # TODO stop and controlled exit
        pass


def read_metadata_file(metadata_queue: PriorityQueue[Metadata]):
    while True:
        # read metadata files
        metadata_paths = WORKDIR.glob('metadata_*.json')

        for metadata_path in metadata_paths:
            with metadata_path.open('r') as file:
                data = json.load(file)
                metadata = Metadata(**data)
                metadata_queue.put((metadata.timestamp, metadata))

            # delete metadata files after reading
            metadata_path.unlink()


def process_batch_request(metadata_queue: PriorityQueue[Metadata]):
    metadata = metadata_queue.get()
    mount_path = WORKDIR / 'mount' / metadata.model_hub_id
    mount_path.mkdir(parents=True, exist_ok=True)

    HuggingFaceCLI.download_model(metadata.model_hub_id)
    TGIServerInstance.start(mount_path)
    TGIClient.run()
    TGIServerInstance.stop()


def main():
    # TODO automatically shut down job after 15 minutes of inactivity
    poll_interval = 60

    status = TGIStatus()
    status_json = status.model_dump_json()
    TGI_STATUS_PATH.write_text(status_json)

    metadata_queue: PriorityQueue[Metadata] = PriorityQueue()

    metadata_reader_thread = Thread(
        target=read_metadata_file, args=(metadata_queue), name='MetadataReaderThread'
    )
    walltime_watcher_thread = Thread(
        target=watch_walltime, name='WalltimeWatcherThread'
    )
    batch_request_processor_thread = Thread(
        target=process_batch_request,
        args=(metadata_queue),
        name='BatchRequestProcessorThread',
    )

    metadata_reader_thread.start()
    walltime_watcher_thread.start()
    batch_request_processor_thread.start()

    metadata_reader_thread.join()
    walltime_watcher_thread.join()
    batch_request_processor_thread.join()

    sleep(poll_interval)


if __name__ == '__main__':
    main()
