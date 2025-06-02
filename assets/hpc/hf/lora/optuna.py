from logging import INFO, basicConfig, getLogger

from optuna import Trial, create_study
from optuna.trial import FrozenTrial
from train import main as train_main

from .settings import FineTuneSettings, OptunaTrialSettings


basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


def objective(trial: Trial, trial_settings: OptunaTrialSettings) -> float:
    trial.suggest_int(**trial_settings.r.model_dump())
    trial.suggest_int(**trial_settings.lora_alpha.model_dump())
    trial.suggest_float(**trial_settings.lora_dropout.model_dump())

    return train_main(trial)


def log(trial: FrozenTrial):
    logger.info(f'Trial number: {trial.number}')
    logger.info(f'F1: {trial.value}')
    logger.info('Hyperparameters:')

    for key, value in trial.params.items():
        logger.info(f'      {key}: {value}')


if __name__ == '__main__':
    # TODO load
    fine_tune_settings: FineTuneSettings = ...
    optuna_settings = fine_tune_settings.optuna_settings

    study = create_study(**optuna_settings.study_settings.model_dump())
    study.enqueue_trial(optuna_settings.trial_start_settings.model_dump())
    study.optimize(objective, n_trials=optuna_settings.n_trials)
    log(study.best_trial)
