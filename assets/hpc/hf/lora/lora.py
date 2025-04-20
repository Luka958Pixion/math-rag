from logging import INFO, basicConfig, getLogger
from pathlib import Path
from subprocess import Popen
from threading import Thread

from decouple import config


WANDB_PROJECT = config('WANDB_PROJECT', default=None)
WANDB_ENTITY = config('WANDB_ENTITY', default=None)
WANDB_NAME = config('WANDB_NAME', default=None)

CLIENT_SIF_PATH = Path('client.sif')
ENV_PATH = Path('.env.hpc.hf.lora')


basicConfig(
    level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
logger = getLogger(__name__)


class FineTuningProcessorThread(Thread):
    def __init__(self):
        super().__init__(name=self.__class__.__name__)

    def run(self):
        cmd = (
            'apptainer run '
            f'--env-file {ENV_PATH} '
            f'--env WANDB_PROJECT={WANDB_PROJECT} '
            f'--env WANDB_ENTITY={WANDB_ENTITY} '
            f'--env WANDB_NAME={WANDB_NAME} '
            f'{CLIENT_SIF_PATH}'
        )
        process = Popen(cmd, check=True, capture_output=False, shell=True)


class WalltimeTrackerThread(Thread):
    def __init__(self):
        super().__init__(name=self.__class__.__name__)

    def run(self):
        pass


def main():
    fine_tuning_processor_thread = FineTuningProcessorThread()
    walltime_tracker_thread = WalltimeTrackerThread()

    fine_tuning_processor_thread.start()
    walltime_tracker_thread.start()

    fine_tuning_processor_thread.join()
    walltime_tracker_thread.join()


if __name__ == '__main__':
    main()
