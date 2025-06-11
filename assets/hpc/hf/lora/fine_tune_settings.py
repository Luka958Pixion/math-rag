from pydantic import BaseModel


class OptunaFloatParam(BaseModel):
    name: str
    low: float
    high: float
    step: float


class OptunaIntParam(BaseModel):
    name: str
    low: int
    high: int
    step: int


class DatasetSettings(BaseModel):
    dataset_name: str
    config_name: str


class ModelSettings(BaseModel):
    model_name: str
    target_modules: list[str]


class OptimizerSettings(BaseModel):
    lr: float
    weight_decay: float


class OptunaStudySettings(BaseModel):
    storage: str
    study_name: str
    direction: str
    load_if_exists: bool


class OptunaTrialStartSettings(BaseModel):
    r: int
    lora_alpha: int
    lora_dropout: float


class OptunaTrialSettings(BaseModel):
    r: OptunaIntParam
    lora_alpha: OptunaIntParam
    lora_dropout: OptunaFloatParam


class OptunaSettings(BaseModel):
    n_trials: int
    metric_name: str
    study_settings: OptunaStudySettings
    trial_start_settings: OptunaTrialStartSettings
    trial_settings: OptunaTrialSettings


class SFTSettings(BaseModel):
    learning_rate: float
    per_device_train_batch_size: int
    gradient_accumulation_steps: int
    num_train_epochs: int
    weight_decay: float
    fp16: bool


class FineTuneSettings(BaseModel):
    dataset_settings: DatasetSettings
    model_settings: ModelSettings
    optimizer_settings: OptimizerSettings
    optuna_settings: OptunaSettings
    sft_settings: SFTSettings
