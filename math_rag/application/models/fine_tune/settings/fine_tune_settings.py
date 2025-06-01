from pydantic import BaseModel

from .dataset_settings import DatasetSettings
from .lora_initial_settings import LoRAInitialSettings
from .lora_settings import LoRASettings
from .model_settings import ModelSettings
from .optuna_settings import OptunaSettings
from .sft_settings import SFTSettings


class FineTuneSettings(BaseModel):
    dataset_settings: DatasetSettings
    lora_initial_settings: LoRAInitialSettings
    lora_settings: LoRASettings
    model_settings: ModelSettings
    optuna_settings: OptunaSettings
    sft_settings: SFTSettings
