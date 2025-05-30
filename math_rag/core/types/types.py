from typing import TypeVar

from math_rag.core.base import BaseDatasetBuildStage, BaseSample


SampleType = TypeVar('SampleType', bound=BaseSample)
DatasetBuildStageType = TypeVar('DatasetBuildStageType', bound=BaseDatasetBuildStage)
