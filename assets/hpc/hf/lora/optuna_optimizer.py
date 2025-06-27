from argparse import ArgumentParser, Namespace
from functools import partial
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from typing import cast
from uuid import UUID

from fine_tune import fine_tune_and_evaluate
from fine_tune_settings import FineTuneSettings
from optuna import Trial, create_study
from optuna.trial import FrozenTrial
from utils import JSONReaderUtil


basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


def objective(
    trial: Trial,
    fine_tune_job_id: UUID,
    fine_tune_settings: FineTuneSettings,
    use_accelerate: bool,
    gpu_indexes: list[int],
) -> float:
    trial_settings = fine_tune_settings.optuna_settings.trial_settings

    trial.suggest_int(**trial_settings.r.model_dump())
    trial.suggest_int(**trial_settings.lora_alpha.model_dump())
    trial.suggest_float(**trial_settings.lora_dropout.model_dump())

    return fine_tune_and_evaluate(
        trial, fine_tune_job_id, fine_tune_settings, use_accelerate, gpu_indexes
    )


def log(trial: FrozenTrial):
    logger.info(f'Trial number: {trial.number}')
    logger.info(f'F1: {trial.value}')
    logger.info('Hyperparameters:')

    for key, value in trial.params.items():
        logger.info(f'  {key}: {value}')


class RawArgs(Namespace):
    fine_tune_job_id: UUID | None
    gpu_indexes: str | None

    use_accelerate: bool


class Args(Namespace):
    fine_tune_job_id: UUID | None
    gpu_indexes: list[int] | None
    use_accelerate: bool


def parse_args() -> Args:
    parser = ArgumentParser()
    parser.add_argument('--fine_tune_job_id', type=UUID, default=None)
    parser.add_argument('--gpu_indexes', type=str, default=None)
    parser.add_argument('--use_accelerate', action='store_true', default=False)

    args = parser.parse_args(namespace=RawArgs())

    if args.gpu_indexes:
        args.gpu_indexes = [int(i) for i in args.gpu_indexes.split(',')]

    return cast(Args, args)


def main():
    args = parse_args()

    if not args.fine_tune_job_id:
        raise ValueError('fine_tune_job_id is required')

    elif args.gpu_indexes is None:
        raise ValueError('gpu_indexes are required')

    elif not args.gpu_indexes:
        raise ValueError('gpu_indexes are empty')

    fine_tune_settings_path = Path(f'input_{args.fine_tune_job_id}.json')

    fine_tune_settings = JSONReaderUtil.read(fine_tune_settings_path, model=FineTuneSettings)
    optuna_settings = fine_tune_settings.optuna_settings
    optuna_settings.study_settings.study_name += f'-fine-tune-job-{args.fine_tune_job_id}'

    study = create_study(**optuna_settings.study_settings.model_dump())
    objective_function = partial(
        objective,
        fine_tune_job_id=args.fine_tune_job_id,
        fine_tune_settings=fine_tune_settings,
        use_accelerate=args.use_accelerate,
        gpu_indexes=args.gpu_indexes,
    )

    study.enqueue_trial(optuna_settings.trial_start_settings.model_dump())
    study.optimize(objective_function, n_trials=optuna_settings.n_trials)
    log(study.best_trial)


if __name__ == '__main__':
    main()
