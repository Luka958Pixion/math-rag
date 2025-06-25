from math_rag.infrastructure.base import BaseDocument

from .dataset_settings_document import DatasetSettingsDocument
from .model_settings_document import ModelSettingsDocument
from .optimizer_settings_document import OptimizerSettingsDocument
from .optuna_settings_document import OptunaSettingsDocument
from .sft_settings_document import SFTSettingsDocument


class FineTuneSettingsDocument(BaseDocument):
    dataset_settings: DatasetSettingsDocument
    model_settings: ModelSettingsDocument
    optimizer_settings: OptimizerSettingsDocument
    optuna_settings: OptunaSettingsDocument
    sft_settings: SFTSettingsDocument
