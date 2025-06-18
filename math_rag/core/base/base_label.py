from abc import ABC

from pydantic import BaseModel


class BaseLabel(BaseModel, ABC):
    pass
