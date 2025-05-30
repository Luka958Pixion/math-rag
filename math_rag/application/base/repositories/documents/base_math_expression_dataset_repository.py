from math_rag.core.enums import MathExpressionDatasetBuildStage
from math_rag.core.models import MathExpressionDataset, MathExpressionSample

from .base_dataset_repository import BaseDatasetRepository
from .base_document_repository import BaseDocumentRepository


class BaseMathExpressionDatasetRepository(
    BaseDatasetRepository[MathExpressionSample, MathExpressionDatasetBuildStage],
    BaseDocumentRepository[MathExpressionDataset],
):
    pass
