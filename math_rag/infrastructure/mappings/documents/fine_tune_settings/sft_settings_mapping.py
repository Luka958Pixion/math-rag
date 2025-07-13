from math_rag.core.models.fine_tune_settings import SFTSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import SFTSettingsDocument


class SFTSettingsMapping(BaseMapping[SFTSettings, SFTSettingsDocument]):
    @staticmethod
    def to_source(target: SFTSettingsDocument) -> SFTSettings:
        return SFTSettings(
            learning_rate=target.learning_rate,
            per_device_train_batch_size=target.per_device_train_batch_size,
            gradient_accumulation_steps=target.gradient_accumulation_steps,
            num_train_epochs=target.num_train_epochs,
            weight_decay=target.weight_decay,
            bf16=target.bf16,
            fp16=target.fp16,
        )

    @staticmethod
    def to_target(source: SFTSettings) -> SFTSettingsDocument:
        return SFTSettingsDocument(
            learning_rate=source.learning_rate,
            per_device_train_batch_size=source.per_device_train_batch_size,
            gradient_accumulation_steps=source.gradient_accumulation_steps,
            num_train_epochs=source.num_train_epochs,
            weight_decay=source.weight_decay,
            bf16=source.bf16,
            fp16=source.fp16,
        )
