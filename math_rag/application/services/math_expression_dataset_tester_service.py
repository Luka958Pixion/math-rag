from logging import getLogger

from math_rag.application.base.repositories.documents import BaseMathExpressionSampleRepository
from math_rag.application.base.services import (
    BaseDatasetPublisherService,
    BaseMathExpressionDatasetPublisherService,
)
from math_rag.application.models.datasets import DatasetMetadataFile
from math_rag.core.models import (
    MathExpressionDataset,
    MathExpressionSample,
)


logger = getLogger(__name__)


class MathExpressionDatasetTesterService(BaseMathExpressionDatasetTesterService):
    def __init__(
        self,
        math_expression_sample_repository: BaseMathExpressionSampleRepository,
    ):
        self.math_expression_sample_repository = math_expression_sample_repository

    async def test(self):
        # TODO MathExpressionDatasetTest Request and Response
        (dataset_id,)
        dataset_name
        split
        model = 'gpt-4.1-nano'
        inference_provider = LLMInferenceProvider.OPEN_AI
        model_provider = LLMProvider.OPEN_AI

    prompt_collection = json.loads(prompt_collection_json_bytes)
