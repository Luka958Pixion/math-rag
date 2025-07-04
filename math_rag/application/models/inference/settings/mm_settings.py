from pydantic import BaseModel

from .basic_mm_settings import BasicMMSettings


class MMSettings(BaseModel):
    basic: BasicMMSettings | None = None
