from label_studio_sdk.label_interface import LabelInterface

from math_rag.application.base.services import BaseLabelConfigBuilderService
from math_rag.infrastructure.models.labels.tags import Choice, Choices, HyperText, Text


TAG_NAME_TO_TYPE = {
    'choices': Choices,
    'hyper_text': HyperText,
    'text': Text,
}


class LabelStudioConfigBuilderService(BaseLabelConfigBuilderService):
    def build(self, field_name_to_tag_name: dict[str, str], label_names: list[str]) -> str:
        tags = {}

        for field_name, tag_name in field_name_to_tag_name.items():
            tag_type = TAG_NAME_TO_TYPE[tag_name]

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
