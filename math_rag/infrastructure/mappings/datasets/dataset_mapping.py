from typing import TypeVar

from datasets import Dataset

from math_rag.application.base.datasets import BaseDataset, BaseSample
from math_rag.infrastructure.base import BaseMapping


T = TypeVar('T', bound=BaseSample)


class DatasetMapping(BaseMapping[BaseDataset[T], Dataset]):
    @staticmethod
    def to_source(target: Dataset) -> BaseDataset[T]:
        raise NotImplementedError()

    @staticmethod
    def to_target(source: BaseDataset[T]) -> Dataset:
        return Dataset.from_list([sample.model_dump() for sample in source.root])
