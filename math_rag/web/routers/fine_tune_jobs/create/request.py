from pydantic import BaseModel, Field

from math_rag.core.models.fine_tune_settings import (
    DatasetSettings,
    FineTuneSettings,
    ModelSettings,
    OptimizerSettings,
    OptunaFloatParam,
    OptunaIntParam,
    OptunaSettings,
    OptunaStudySettings,
    OptunaTrialSettings,
    OptunaTrialStartSettings,
    SFTSettings,
)


_default_fine_tune_settings = FineTuneSettings(
    dataset_settings=DatasetSettings(
        dataset_name='math_expression_dataset', config_name='b5887579-5742-4e0f-91ce-2fae26bf2c01'
    ),
    model_settings=ModelSettings(
        model_name='meta-llama/Llama-3.1-8B-Instruct',
        target_modules=['q_proj', 'v_proj'],
        max_tokens=20,
    ),
    optimizer_settings=OptimizerSettings(lr=0.0002, weight_decay=0.01),
    optuna_settings=OptunaSettings(
        n_trials=1,
        metric_name='f1',
        study_settings=OptunaStudySettings(
            storage='sqlite:///optuna_lora_study.db',
            study_name='optuna-lora-study',
            direction='maximize',
            load_if_exists=True,
        ),
        trial_start_settings=OptunaTrialStartSettings(r=8, lora_alpha=16, lora_dropout=0.0),
        trial_settings=OptunaTrialSettings(
            r=OptunaIntParam(name='r', low=2, high=16, step=2),
            lora_alpha=OptunaIntParam(name='lora_alpha', low=4, high=68, step=8),
            lora_dropout=OptunaFloatParam(name='lora_dropout', low=0.0, high=0.3, step=0.05),
        ),
    ),
    sft_settings=SFTSettings(
        learning_rate=2e-4,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=4,
        num_train_epochs=1,
        weight_decay=0.01,
        fp16=True,
    ),
)


class Request(BaseModel):
    fine_tune_settings: FineTuneSettings = Field(default=_default_fine_tune_settings)
