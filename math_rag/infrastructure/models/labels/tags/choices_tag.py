from typing import Literal

from pydantic import Field

from math_rag.infrastructure.base import BaseTag


class ChoicesTag(BaseTag):
    """
    Label Studio <Choices> tag parameters

    Reference:
        https://labelstud.io/tags/choices
    """

    name: str
    to_name: str = Field(..., alias='toName')
    choice: Literal['single', 'single-radio', 'multiple'] = 'single'
    show_inline: bool = Field(False, alias='showInline')
    required: bool = False
    required_message: str | None = Field(None, alias='requiredMessage')
    visible_when: (
        Literal['region-selected', 'no-region-selected', 'choice-selected', 'choice-unselected']
        | None
    ) = Field(None, alias='visibleWhen')
    when_tag_name: str | None = Field(None, alias='whenTagName')
    when_label_value: str | None = Field(None, alias='whenLabelValue')
    when_choice_value: str | None = Field(None, alias='whenChoiceValue')
    per_region: bool = Field(False, alias='perRegion')
    per_item: bool = Field(False, alias='perItem')
    value: str | None = None
    allow_nested: bool = Field(False, alias='allowNested')

    model_config = {'populate_by_name': True, 'populate_by_alias': True}
