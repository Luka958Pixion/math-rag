from typing import Literal

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
    zoom: bool = False
    negative_zoom: bool = Field(False, alias='negativeZoom')
    zoom_by: float = Field(1.1, alias='zoomBy')
    grid: bool = False
    grid_size: int = Field(30, alias='gridSize')
    grid_color: str = Field('#EEEEF4', alias='gridColor')
    zoom_control: bool = Field(False, alias='zoomControl')
    brightness_control: bool = Field(False, alias='brightnessControl')
    contrast_control: bool = Field(False, alias='contrastControl')
    rotate_control: bool = Field(False, alias='rotateControl')
    crosshair: bool = False
    horizontal_alignment: Literal['left', 'center', 'right'] = Field(
        'left', alias='horizontalAlignment'
    )
    vertical_alignment: Literal['top', 'center', 'bottom'] = Field('top', alias='verticalAlignment')
    default_zoom: Literal['auto', 'original', 'fit'] = Field('fit', alias='defaultZoom')
    cross_origin: Literal['none', 'anonymous', 'use-credentials'] = Field(
        'none', alias='crossOrigin'
    )

    model_config = {'populate_by_name': True, 'populate_by_alias': True}
