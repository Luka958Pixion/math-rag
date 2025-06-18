from typing import Literal

from label_studio_sdk.label_interface.base import LabelStudioTag
from pydantic import Field

from math_rag.infrastructure.base import BaseTag


class HyperTextTag(BaseTag):
    """
    Label Studio <HyperText> tag parameters

    Reference:
        https://labelstud.io/tags/hypertext
    """

    name: str
    value: str | None = None
    value_type: Literal['url', 'text'] = Field('text', alias='valueType')
    inline: bool = False
    save_text_result: Literal['yes', 'no'] | None = Field(None, alias='saveTextResult')
    encoding: Literal['none', 'base64', 'base64unicode'] = 'none'
    selection_enabled: bool = Field(True, alias='selectionEnabled')
    clickable_links: bool = Field(False, alias='clickableLinks')
    highlight_color: str | None = Field(None, alias='highlightColor')
    show_labels: bool | None = Field(None, alias='showLabels')
    granularity: Literal['symbol', 'word', 'sentence', 'paragraph'] | None = None

    model_config = {'populate_by_name': True, 'populate_by_alias': True}

    def to_label_studio_tag(self) -> LabelStudioTag:
        return LabelStudioTag(
            tag='HyperText',
            attr=self.model_dump(by_alias=True),
        )
