from functools import partial
from logging import INFO, basicConfig, getLogger
from pathlib import Path
from uuid import UUID

from decouple import Config, RepositoryEnv
from fine_tune import fine_tune_and_evaluate
from fine_tune_settings import FineTuneSettings
from optuna import Trial, create_study
from optuna.trial import FrozenTrial
from utils import YamlReaderUtil


config = Config(repository=RepositoryEnv('.env.hpc'))

FINE_TUNE_JOB_ID = config('FINE_TUNE_JOB_ID', cast=UUID)
FINE_TUNE_SETTINGS_PATH = Path(f'input_{FINE_TUNE_JOB_ID}.yaml')


basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


def objective(trial: Trial, fine_tune_settings: FineTuneSettings) -> float:
    trial_settings = fine_tune_settings.optuna_settings.trial_settings

    trial.suggest_int(**trial_settings.r.model_dump())
    trial.suggest_int(**trial_settings.lora_alpha.model_dump())
    trial.suggest_float(**trial_settings.lora_dropout.model_dump())

    return fine_tune_and_evaluate(trial, fine_tune_settings, FINE_TUNE_JOB_ID)


def log(trial: FrozenTrial):
    logger.info(f'Trial number: {trial.number}')
    logger.info(f'F1: {trial.value}')
    logger.info('Hyperparameters:')

    for key, value in trial.params.items():
        logger.info(f'  {key}: {value}')


def main():
    fine_tune_settings = YamlReaderUtil.read(FINE_TUNE_SETTINGS_PATH, model=FineTuneSettings)
    optuna_settings = fine_tune_settings.optuna_settings

    study = create_study(**optuna_settings.study_settings.model_dump())
    study.enqueue_trial(optuna_settings.trial_start_settings.model_dump())
    study.optimize(
        partial(objective, fine_tune_settings=fine_tune_settings), n_trials=optuna_settings.n_trials
    )
    log(study.best_trial)


if __name__ == '__main__':
    main()
