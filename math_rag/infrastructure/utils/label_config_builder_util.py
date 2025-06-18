from enum import Enum
from typing import TypeVar

from label_studio_sdk.label_interface import LabelInterface

from math_rag.infrastructure.models.labels.tags import Choice, Choices, HyperText, Text
from math_rag.infrastructure.types.labels.tags import TagType


LabelType = TypeVar('LabelType', bound=Enum)


class LabelConfigBuilderUtil:
    @staticmethod
    def build(field_name_to_tag_type: dict[str, type[TagType]], label_names: list[str]) -> str:
        tags = {}

        for field_name, tag_type in field_name_to_tag_type.items():
            if type(tag_type) is Choices:
                choices = [Choice(value=label_name) for label_name in label_names]
                tags[field_name] = Choices(name=field_name, choice='single', choices=choices)

            elif type(tag_type) is HyperText:
                tags[field_name] = HyperText(name=field_name, selection_enabled=False)

            elif type(tag_type) is Text:
                tags[field_name] = Text(name=field_name, selection_enabled=False)

            else:
                raise ValueError()

        return LabelInterface.create(tags)
