import subprocess

from argparse import ArgumentParser, Namespace
from functools import partial
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from uuid import UUID

from fine_tune_settings import FineTuneSettings, OptunaTrialSettings
from optuna import Trial, create_study
from optuna.trial import FrozenTrial
from results import Result
from utils import JSONReaderUtil


basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


def objective(
    trial: Trial,
    fine_tune_job_id: UUID,
    optuna_trial_settings: OptunaTrialSettings,
    gpu_indexes: str,
    num_gpus: int,
    use_accelerate: bool,
) -> float:
    trial.suggest_int(**optuna_trial_settings.r.model_dump())
    trial.suggest_int(**optuna_trial_settings.lora_alpha.model_dump())
    trial.suggest_float(**optuna_trial_settings.lora_dropout.model_dump())

    fine_tune_settings_path = Path(f'input_{fine_tune_job_id}.json')
    fine_tune_result_path = Path(f'output_{fine_tune_job_id}.json')

    if use_accelerate:
        num_machines = 1
        mixed_precision = 'no'
        dynamo_backend = 'no'

        cmd = (
            'accelerate launch '
            f'--num_processes {num_gpus} '
            f'--num_machines {num_machines} '
            f'--mixed_precision {mixed_precision} '
            f'--dynamo_backend {dynamo_backend} '
            'fine_tune.py '
            f'--fine_tune_job_id {fine_tune_job_id} '
            f'--fine_tune_settings_path {fine_tune_settings_path} '
            f'--fine_tune_result_path {fine_tune_result_path} '
            f'--trial_number {trial.number} '
            f'--gpu_indexes {gpu_indexes} '
            '--use_accelerate'
        )

    else:
        cmd = (
            'python fine_tune.py '
            f'--fine_tune_job_id {fine_tune_job_id} '
            f'--fine_tune_settings_path {fine_tune_settings_path} '
            f'--fine_tune_result_path {fine_tune_result_path} '
            f'--trial_number {trial.number} '
            f'--gpu_indexes {gpu_indexes} '
        )

    subprocess.run(cmd, check=True, text=True, shell=True)
    result = JSONReaderUtil.read(fine_tune_result_path, model=Result)

    for trial_result in result.trial_results:
        if trial_result.number == trial.number:
            return trial_result.score

    raise ValueError(f'Trial with number {trial.number} not found')


def log(trial: FrozenTrial):
    logger.info(f'Trial number: {trial.number}')
    logger.info(f'F1: {trial.value}')
    logger.info('Hyperparameters:')

    for key, value in trial.params.items():
        logger.info(f'  {key}: {value}')


class Args(Namespace):
    fine_tune_job_id: UUID
    gpu_indexes: str
    num_gpus: int
    use_accelerate: bool


def parse_args() -> Args:
    parser = ArgumentParser()
    parser.add_argument('--fine_tune_job_id', type=UUID, required=True)
    parser.add_argument('--gpu_indexes', type=str, required=True)
    parser.add_argument('--num_gpus', type=int, required=True)
    parser.add_argument('--use_accelerate', action='store_true', default=False)

    return parser.parse_args(namespace=Args())


def main():
    args = parse_args()

    fine_tune_settings_path = Path(f'input_{args.fine_tune_job_id}.json')
    fine_tune_settings = JSONReaderUtil.read(fine_tune_settings_path, model=FineTuneSettings)
    optuna_settings = fine_tune_settings.optuna_settings
    optuna_settings.study_settings.study_name += f'-fine-tune-job-{args.fine_tune_job_id}'

    study = create_study(**optuna_settings.study_settings.model_dump())
    objective_function = partial(
        objective,
        fine_tune_job_id=args.fine_tune_job_id,
        optuna_trial_settings=optuna_settings.trial_settings,
        gpu_indexes=args.gpu_indexes,
        num_gpus=args.num_gpus,
        use_accelerate=args.use_accelerate,
    )

    study.enqueue_trial(optuna_settings.trial_start_settings.model_dump())
    study.optimize(objective_function, n_trials=optuna_settings.n_trials)
    log(study.best_trial)


if __name__ == '__main__':
    main()
