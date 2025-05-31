from abc import ABC

from pydantic import BaseModel


class BaseSample(BaseModel, ABC):
    pass
