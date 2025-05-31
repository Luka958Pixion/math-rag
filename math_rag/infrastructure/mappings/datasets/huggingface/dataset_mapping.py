from typing import TypeVar

from datasets import Dataset, DatasetInfo

from math_rag.core.models import MathExpressionDataset, MathExpressionSample
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.utils import DatasetFeatureExtractorUtil


class MathExpressionDatasetMapping(BaseMapping[MathExpressionDataset, Dataset]):
    @staticmethod
    def to_source(target: Dataset) -> MathExpressionDataset:
        raise NotImplementedError()

    @staticmethod
    def to_target(source: MathExpressionDataset) -> Dataset:
        features = DatasetFeatureExtractorUtil.extract(MathExpressionSample)
        info = DatasetInfo(license='mit', features=features)

        return Dataset.from_list(
            mapping=[sample.model_dump(mode='json') for sample in source.samples],
            features=features,
            info=info,
            split=None,
        )
