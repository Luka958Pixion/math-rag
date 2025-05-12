from abc import ABC
from typing import Generic, TypeVar

from pydantic import RootModel

from .base_sample import BaseSample


T = TypeVar('T', bound=BaseSample)


class BaseDataset(RootModel[list[T]], Generic[T], ABC):
    pass
