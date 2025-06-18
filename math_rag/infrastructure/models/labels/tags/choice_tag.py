from label_studio_sdk.label_interface.base import LabelStudioTag
from pydantic import Field

from math_rag.infrastructure.base import BaseTag


class ChoiceTag(BaseTag):
    """
    Label Studio <Choice> tag parameters

    Reference:
        https://labelstud.io/tags/choice
    """

    value: str
    selected: bool | None = None
    alias_: str | None = Field(None, alias='alias')
    style: str | None = None
    hotkey: str | None = None
    html: str | None = None
    hint: str | None = None
    color: str | None = None

    model_config = {'populate_by_name': True, 'populate_by_alias': True}

    def to_label_studio_tag(self) -> LabelStudioTag:
        return LabelStudioTag(
            tag='Choice',
            attr=self.model_dump(by_alias=True),
        )
