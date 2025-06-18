from pydantic import Field

from math_rag.infrastructure.base import BaseTag


class ImageTag(BaseTag):
    """
    Label Studio <Image> tag parameters

    Reference:
        https://labelstud.io/tags/image
    """

    name: str
    value: str
    value_list: str | None = Field(None, alias='valueList')
    smoothing: bool = False
    width: str = '100%'
    max_width: str = Field('750px', alias='maxWidth')

    model_config = {'populate_by_name': True, 'populate_by_alias': True}
