from logging import getLogger
from uuid import UUID

from math_rag.application.assistants import MathExpressionLabelerAssistant
from math_rag.application.base.services import (
    BaseDatasetLoaderService,
    BaseMathExpressionDatasetTesterService,
)
from math_rag.application.enums.inference import LLMInferenceProvider, LLMProvider
from math_rag.application.models.assistants import MathExpressionLabelerAssistantInput
from math_rag.application.models.inference import LLMPromptCollection
from math_rag.core.models import (
    MathExpressionDataset,
    MathExpressionSample,
)


logger = getLogger(__name__)

DATASET_NAME = MathExpressionDataset.__name__.lower()
DATASET_METADATA_FILE_NAME = 'prompt.json'
SPLIT_NAME = 'test'


class MathExpressionDatasetTesterService(BaseMathExpressionDatasetTesterService):
    def __init__(
        self,
        dataset_loader_service: BaseDatasetLoaderService,
        math_expression_labeler_assistant: MathExpressionLabelerAssistant,
    ):
        self.dataset_loader_service = dataset_loader_service
        self.math_expression_labeler_assistant = math_expression_labeler_assistant

    async def test(
        self,
        dataset_id: UUID,
        model: str,
        inference_provider: LLMInferenceProvider,
        model_provider: LLMProvider,
    ):
        # load dataset
        split_name_to_samples, dataset_metadata_file = self.dataset_loader_service.load(
            dataset_id=dataset_id,
            dataset_name=DATASET_NAME,
            dataset_metadata_file_name=DATASET_METADATA_FILE_NAME,
            sample_type=MathExpressionSample,
            max_retries=3,
        )
        prompt_collection = LLMPromptCollection.model_validate_json(dataset_metadata_file.content)

        # override assistant
        self.math_expression_labeler_assistant.system_prompt = prompt_collection.system
        self.math_expression_labeler_assistant.user_prompt = prompt_collection.user
        self.math_expression_labeler_assistant.model = model
        self.math_expression_labeler_assistant.inference_provider = inference_provider
        self.math_expression_labeler_assistant.model_provider = model_provider

        # test
        samples = split_name_to_samples[SPLIT_NAME]
        inputs = [MathExpressionLabelerAssistantInput(latex=sample.katex) for sample in samples]
        outputs = await self.math_expression_labeler_assistant.batch_assist(
            inputs, use_scheduler=True
        )
