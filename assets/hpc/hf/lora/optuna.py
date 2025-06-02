from logging import INFO, basicConfig, getLogger

from optuna import Trial, create_study
from train import main as train_main


basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


N_TRIALS = 20
R = ...
LORA_ALPHA = ...
LORA_DROPOUT = ...
DIRECTION = ...


def objective(trial: Trial) -> float:
    trial.suggest_int('r', 4, 32, step=1)  # TODO
    trial.suggest_int('lora_alpha', 8, 64, step=8)
    trial.suggest_float('lora_dropout', 0.0, 0.3, step=0.05)

    return train_main(trial)


if __name__ == '__main__':
    storage_name = 'sqlite:///optuna_lora_study.db'
    study_name = 'lora_hyperparam_search'

    study = create_study(
        study_name=study_name, storage=storage_name, direction=DIRECTION, load_if_exists=True
    )
    study.enqueue_trial(
        {
            'r': R,
            'lora_alpha': LORA_ALPHA,
            'lora_dropout': LORA_DROPOUT,
        }
    )
    study.optimize(objective, n_trials=N_TRIALS)

    best_trial = study.best_trial
    logger.info('Best trial')
    logger.info(f'  number: {best_trial.number}')
    logger.info(f'  F1: {best_trial.value}')
    logger.info(f'  hyperparameters')

    for key, value in best_trial.params.items():
        logger.info(f'      {key}: {value}')
