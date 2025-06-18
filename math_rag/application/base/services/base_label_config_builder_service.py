from abc import ABC, abstractmethod

from math_rag.infrastructure.types.labels.tags import TagType


class BaseLabelConfigBuilderService(ABC):
    @abstractmethod
    def build(
        self, field_name_to_tag_type: dict[str, type[TagType]], label_names: list[str]
    ) -> str:
        pass
