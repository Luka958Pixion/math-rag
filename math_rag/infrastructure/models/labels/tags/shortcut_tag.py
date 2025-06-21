from typing import Literal

from pydantic import Field

from math_rag.infrastructure.base import BaseTag


class ShortcutTag(BaseTag):
    """
    Label Studio <Text> tag parameters

    Reference:
        https://labelstud.io/tags/shortcut
    """

    value: str
    alias: str
    hotkey: str
    background: str = '#333333'

    model_config = {'populate_by_name': True, 'populate_by_alias': True}
