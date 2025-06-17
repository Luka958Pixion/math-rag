from typing import Literal

from pydantic import Field

from math_rag.infrastructure.base import BaseTag


class Text(BaseTag):
    """
    Label Studio <Text> tag parameters

    Reference:
        https://labelstud.io/tags/text
    """

    name: str
    value: str | None = None
    value_type: Literal['url', 'text'] = Field('text', alias='valueType')
    save_text_result: Literal['yes', 'no'] | None = Field(None, alias='saveTextResult')
    encoding: Literal['none', 'base64', 'base64unicode'] = 'none'
    selection_enabled: bool = Field(True, alias='selectionEnabled')
    highlight_color: str | None = Field(None, alias='highlightColor')
    show_labels: bool | None = Field(None, alias='showLabels')
    granularity: Literal['symbol', 'word', 'sentence', 'paragraph'] | None = None

    model_config = {'populate_by_name': True, 'populate_by_alias': True}
