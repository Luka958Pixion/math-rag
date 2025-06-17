from abc import ABC

from pydantic import BaseModel


class BaseTag(ABC, BaseModel):
    pass
