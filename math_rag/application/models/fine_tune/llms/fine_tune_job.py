from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .dataset_settings import DatasetSettings
from .lora_settings import LoRASettings
from .model_settings import ModelSettings
from .optuna_settings import OptunaSettings


class FineTuneJob(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    dataset_settings: DatasetSettings
    lora_settings: LoRASettings
    model_settings: ModelSettings
    optuna_settings: OptunaSettings
