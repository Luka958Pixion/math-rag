import json
import os
import signal
import subprocess

from enum import Enum
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from time import sleep
from types import FrameType

from decouple import config
from httpx import Client


WORKDIR = config('PBS_O_WORKDIR', cast=Path, default=Path.cwd())
MODEL_HUB_ID = config('MODEL_HUB_ID')

HTTP_PROXY = 'http://10.150.1.1:3128'
HTTPS_PROXY = 'http://10.150.1.1:3128'
TGI_BASE_URL = 'http://0.0.0.0:8000'

TGI_STATUS_PATH = Path('tgi_status.json')
TGI_STATUS_TMP_PATH = TGI_STATUS_PATH.with_suffix('.tmp')

basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


class TGIStatus(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    FINISHED = 'finished'
    FAILED = 'failed'


class TGIStatusTracker:
    def __init__(self):
        self._statuses: dict[str, TGIStatus] = {}

    def set_status(self, task_id: str, status: TGIStatus):
        self._statuses[task_id] = status

        with TGI_STATUS_TMP_PATH.open('w') as file:
            json.dump({'status': status.value}, file)

        os.replace(TGI_STATUS_TMP_PATH, TGI_STATUS_PATH)

    def get_status(self, task_id: str) -> TGIStatus | None:
        return self._statuses.get(task_id)

    def remove_status(self, task_id: str):
        if task_id in self._statuses:
            del self._statuses[task_id]


class HuggingFaceCLI:
    @staticmethod
    def download_model():
        env = os.environ.copy()
        env['http_proxy'] = HTTP_PROXY
        env['https_proxy'] = HTTPS_PROXY

        bind = f'{WORKDIR}/data:/data'
        cmd = f'apptainer run --nv --bind {bind} hf_cli.sif'
        subprocess.run(cmd, check=True, capture_output=False, shell=True, env=env)


class TGIServerInstance:
    @staticmethod
    def start(data_path: Path, client: Client):
        logger.info('Starting TGI server...')

        bind = f'{data_path}:/model'
        cmd = f'apptainer instance start --nv --bind {bind} server.sif tgi_server_instance'
        subprocess.run(cmd, check=True, capture_output=False, shell=True)

        logger.info('Waiting for TGI server to become healthy...')

        while True:
            response = client.get(TGI_BASE_URL + '/health', timeout=3)

            if response.status_code == 200:
                logger.info('TGI server is healthy.')
                break

            logger.info(
                f'Health check returned status {response.status_code}. Retrying in 5s...'
            )
            sleep(5)

    @staticmethod
    def stop():
        cmd = f'apptainer instance stop tgi_server_instance'
        subprocess.run(cmd, check=True, capture_output=False, shell=True)


class TGIClient:
    @staticmethod
    def run():
        env = os.environ.copy()
        env['TGI_BASE_URL'] = TGI_BASE_URL
        env.pop('MODEL_HUB_ID')

        cmd = 'apptainer run --env-file .env.hpc.hf.tgi client.sif'
        subprocess.run(cmd, check=True, capture_output=False, shell=True, env=env)


def handle_sigusr1(signum: int, frame: FrameType | None):
    logger.info('Received SIGUSR1. Running TGI client...')
    logger.info('signum: ', signum)
    logger.info('frame: ', frame)

    TGIClient.run()
    TGIServerInstance.stop()

    exit(0)


def main():
    os.chdir(WORKDIR)
    signal.signal(signal.SIGUSR1, handle_sigusr1)

    data_path = WORKDIR / 'data' / MODEL_HUB_ID
    data_path.mkdir(parents=True, exist_ok=True)

    HuggingFaceCLI.download_model()

    client = Client()
    TGIServerInstance.start(data_path, client)

    logger.info(f'Waiting for SIGUSR1 (pid {os.getpid()}) to start TGI client...')
    signal.pause()


if __name__ == '__main__':
    main()
