from pydantic import BaseModel

from .dataset_settings import DatasetSettings
from .model_settings import ModelSettings
from .optimizer_settings import OptimizerSettings
from .optuna_settings import OptunaSettings
from .sft_settings import SFTSettings


class FineTuneSettings(BaseModel):
    dataset_settings: DatasetSettings
    model_settings: ModelSettings
    optimizer_settings: OptimizerSettings
    optuna_settings: OptunaSettings
    sft_settings: SFTSettings
