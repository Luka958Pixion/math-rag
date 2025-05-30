from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseMathExpressionDatasetRepository
from math_rag.core.enums import MathExpressionDatasetBuildStage
from math_rag.core.models import MathExpressionDataset, MathExpressionSample
from math_rag.infrastructure.mappings.documents import DatasetMapping
from math_rag.infrastructure.models.documents import DatasetDocument

from .dataset_repository import DatasetRepository


class MathExpressionDatasetRepository(
    BaseMathExpressionDatasetRepository,
    DatasetRepository[
        MathExpressionSample,
        MathExpressionDatasetBuildStage,
        MathExpressionDataset,
        DatasetDocument,
        DatasetMapping,
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
