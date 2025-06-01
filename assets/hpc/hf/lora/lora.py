import os
import subprocess

from datetime import timedelta
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from threading import Event, Thread
from time import sleep


# current job
PBS_JOB_ID = os.environ['PBS_JOBID']

# squid proxy
HTTP_PROXY = 'http://10.150.1.1:3128'
HTTPS_PROXY = 'http://10.150.1.1:3128'

# thresholds
WALL_TIME_THRESHOLD = timedelta(minutes=30)

# paths
LORA_SIF_PATH = Path('lora.sif')
ENV_PATH = Path('.env.hpc')


basicConfig(level=INFO, format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
logger = getLogger(__name__)


class FineTuningProcessorThread(Thread):
    def __init__(self, training_stop_event: Event, training_done_event: Event):
        super().__init__(name=self.__class__.__name__)

        self._training_stop_event = training_stop_event
        self._training_done_event = training_done_event

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        # TODO - switch logic for different providers and models for each of them
        MODEL_NAME = ...
        TOKENIZER_NAME = ...
        cmd = (
            'apptainer run '
            '--nv '
            f'--env-file {ENV_PATH} '
            f'--env MODEL_NAME={MODEL_NAME} '
            f'--env TOKENIZER_NAME={TOKENIZER_NAME} '
            f'--env http_proxy={HTTP_PROXY} '
            f'--env https_proxy={HTTPS_PROXY} '
            f'{LORA_SIF_PATH}'
        )
        # process = Popen(cmd, shell=True)
        # exit_status = cli_state.wait(process)

        self._training_done_event.set()
        logger.info(f'{self.__class__.__name__} exited')


class WallTimeTrackerThread(Thread):
    def __init__(self, training_stop_event: Event, training_done_event: Event):
        super().__init__(name=self.__class__.__name__)

        self._training_stop_event = training_stop_event
        self._training_done_event = training_done_event

    def run(self):
        logger.info(f'{self.__class__.__name__} started')

        DELAY = 3 * 60
        cmd = (
            f'qstat -f {PBS_JOB_ID} | '
            "awk -F'= ' "
            "'/Resource_List.walltime/ { walltime = $2 } "
            '/resources_used.walltime/ { used = $2 } '
            'END { print walltime "\\n" used }\''
        )

        while True:
            if self._training_done_event.is_set():
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
                self._training_stop_event.set()
                break

            sleep(DELAY)

        logger.info(f'{self.__class__.__name__} exited')


def main():
    # initialization
    training_stop_event = Event()
    training_done_event = Event()

    # threads
    fine_tuning_processor_thread = FineTuningProcessorThread(
        training_stop_event, training_done_event
    )
    wall_time_tracker_thread = WallTimeTrackerThread(training_stop_event, training_done_event)

    fine_tuning_processor_thread.start()
    wall_time_tracker_thread.start()

    fine_tuning_processor_thread.join()
    wall_time_tracker_thread.join()


if __name__ == '__main__':
    main()
