from abc import ABC, abstractmethod
from enum import Enum


class BaseDatasetBuildStage(str, Enum, ABC):
    @classmethod
    @abstractmethod
    def default(cls):
        pass
