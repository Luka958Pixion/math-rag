from abc import ABC

from pydantic import BaseModel


class BaseLabelTask(BaseModel, ABC):
    pass
