import signal
import subprocess

from logging import INFO, basicConfig, getLogger
from os import environ, getpid
from pathlib import Path
from time import sleep
from types import FrameType

from decouple import config
from httpx import Client, RequestError


PBS_O_WORKDIR = config('PBS_O_WORKDIR', cast=Path)
MODEL_HUB_ID = config('MODEL_HUB_ID')

basicConfig(
    level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
logger = getLogger(__name__)


def handle_sigusr1(signum: int, frame: FrameType | None):
    logger.info('Received SIGUSR1. Running TGI client...')

    subprocess.run(
        ['apptainer', 'run', '--env-file', '.env.hpc.hf.tgi', 'tgi_client.sif']
    )
    subprocess.run(['apptainer', 'instance', 'stop', 'tgi_server_instance'])

    exit(0)


signal.signal(signal.SIGUSR1, handle_sigusr1)

environ['PYTHONUNBUFFERED'] = '1'
environ['TGI_BASE_URL'] = 'http://0.0.0.0:8000'
environ['http_proxy'] = 'http://10.150.1.1:3128'
environ['https_proxy'] = 'http://10.150.1.1:3128'


data_path = PBS_O_WORKDIR / 'data' / MODEL_HUB_ID
data_path.mkdir(parents=True, exist_ok=True)

subprocess.run(
    [
        'apptainer',
        'run',
        '--nv',
        '--bind',
        f'{PBS_O_WORKDIR / "data"}:/data',
        'hf_cli.sif',
    ],
    check=True,
)


environ.pop('http_proxy')
environ.pop('https_proxy')


subprocess.run(
    [
        'apptainer',
        'instance',
        'start',
        '--nv',
        '--bind',
        f'{data_path}:/model',
        'tgi_server.sif',
        'tgi_server_instance',
    ],
    check=True,
)


logger.info('Waiting for the TGI server to become healthy...')
client = Client()

while True:
    response = client.get('http://0.0.0.0:8000/health', timeout=2)

    if response.status_code == 200:
        logger.info('TGI server is healthy.')
        break

    logger.info(
        f'Health check returned status {response.status_code}. Retrying in 5s...'
    )
    sleep(5)


logger.info(f'Waiting for SIGUSR1 (pid {getpid()}) to start TGI client...')
signal.pause()
