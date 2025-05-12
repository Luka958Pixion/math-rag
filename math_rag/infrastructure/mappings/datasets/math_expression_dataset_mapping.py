from datasets import Dataset

from math_rag.application.models.datasets import MathExpressionDataset
from math_rag.infrastructure.base import BaseMapping


class MathExpressionDatasetMapping(BaseMapping[MathExpressionDataset, Dataset]):
    @staticmethod
    def to_source(target: Dataset) -> MathExpressionDataset:
        raise NotImplementedError()

    @staticmethod
    def to_target(source: MathExpressionDataset) -> Dataset:
        return Dataset.from_list([sample.model_dump() for sample in source.root])
