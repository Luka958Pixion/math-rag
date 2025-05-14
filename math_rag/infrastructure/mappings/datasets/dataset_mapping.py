from typing import TypeVar

from datasets import Dataset, DatasetInfo

from math_rag.application.base.datasets import BaseDataset, BaseSample
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.utils import DatasetFeatureExtractorUtil


T = TypeVar('T', bound=BaseSample)


class DatasetMapping(BaseMapping[BaseDataset[T], Dataset]):
    @staticmethod
    def to_source(target: Dataset) -> BaseDataset[T]:
        raise NotImplementedError()

    @staticmethod
    def to_target(source: BaseDataset[T], *, sample_type: type[T]) -> Dataset:
        features = DatasetFeatureExtractorUtil.extract(sample_type)
        info = DatasetInfo(license='mit', features=features)

        return Dataset.from_list(
            mapping=[sample.model_dump(mode='json') for sample in source.root],
            features=features,
            info=info,
            split=None,
        )
