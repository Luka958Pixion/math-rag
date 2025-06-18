from label_studio_sdk.label_interface import LabelInterface

from math_rag.application.base.services import BaseLabelConfigBuilderService
from math_rag.infrastructure.models.labels.tags import (
    ChoicesTag,
    ChoiceTag,
    HyperTextTag,
    ImageTag,
    TextTag,
)


TAG_NAME_TO_TYPE: dict[str, type] = {
    'choices': ChoicesTag,
    'hyper_text': HyperTextTag,
    'text': TextTag,
}


def _serialize_attrs(attrs: dict) -> dict[str, str]:
    """
    Convert attribute values to strings for XML serialization.
    Booleans become lowercase 'true' or 'false', others are str().
    None values are dropped.
    """
    serialized: dict[str, str] = {}

    for key, value in attrs.items():
        if value is None:
            continue

        if isinstance(value, bool):
            serialized[key] = 'true' if value else 'false'
        else:
            serialized[key] = str(value)

    return serialized


class LabelStudioConfigBuilderService(BaseLabelConfigBuilderService):
    def build(self, field_name_to_tag_name: dict[str, str], label_names: list[str]) -> str:
        tags: dict[str, tuple] = {}
        field_names = list(field_name_to_tag_name.keys())

        for field_name, tag_name in field_name_to_tag_name.items():
            tag_type = TAG_NAME_TO_TYPE[tag_name]

            if tag_type is ChoicesTag:
                other_field_names = [name for name in field_names if name != field_name]
                to_name = ','.join(other_field_names)
                choices_tag = ChoicesTag(name=field_name, to_name=to_name, choice='single')
                choices_tag_attrs = choices_tag.model_dump(by_alias=True)
                choices_tag_attrs_serial = _serialize_attrs(choices_tag_attrs)

                choice_tuples = []

                for name in label_names:
                    choice_tag = ChoiceTag(value=name)
                    choice_tag_attrs = choice_tag.model_dump(by_alias=True)
                    choice_tag_attrs_serial = _serialize_attrs(choice_tag_attrs)
                    choice_tuples.append(('Choice', choice_tag_attrs_serial, ()))

                tags[field_name] = ('Choices', choices_tag_attrs_serial, tuple(choice_tuples))

            elif tag_type is HyperTextTag:
                hyper_text_tag = HyperTextTag(
                    name=field_name, selection_enabled=False, inline=False
                )
                hyper_text_tag_attrs = hyper_text_tag.model_dump(by_alias=True)
                hyper_text_tag_attrs_serial = _serialize_attrs(hyper_text_tag_attrs)
                tags[field_name] = ('HyperText', hyper_text_tag_attrs_serial, ())

            elif tag_type is TextTag:
                text_tag = TextTag(name=field_name, selection_enabled=False)
                text_tag_attrs = text_tag.model_dump(by_alias=True)
                text_tag_attrs_serial = _serialize_attrs(text_tag_attrs)
                tags[field_name] = ('Text', text_tag_attrs_serial, ())

            else:
                raise ValueError(f'Unknown tag type: {tag_name}')

        # insert headers before each element
        tags_updated: dict[str, tuple] = {}

        for field_name in field_names:
            tags_updated[f'header_{field_name}'] = ('Header', {'value': field_name.title()}, ())
            tags_updated[field_name] = tags[field_name]

        return LabelInterface.create(tags_updated, pretty=False)
