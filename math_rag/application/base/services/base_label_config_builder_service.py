from abc import ABC, abstractmethod


class BaseLabelConfigBuilderService(ABC):
    @abstractmethod
    def build(self, field_name_to_tag_name: dict[str, str], label_names: list[str]) -> str:
        pass
