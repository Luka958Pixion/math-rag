from logging import getLogger
from uuid import UUID

from math_rag.application.assistants import MathExpressionLabelerAssistant
from math_rag.application.base.services import (
    BaseDatasetLoaderService,
    BaseMathExpressionDatasetTesterService,
)
from math_rag.application.enums.inference import LLMInferenceProvider, LLMModelProvider
from math_rag.application.models.assistants import MathExpressionLabelerAssistantInput
from math_rag.application.models.inference import LLMPromptCollection
from math_rag.core.models import (
    MathExpressionDataset,
    MathExpressionDatasetTest,
    MathExpressionDatasetTestResult,
    MathExpressionLabel,
    MathExpressionSample,
)


logger = getLogger(__name__)

DATASET_NAME = MathExpressionDataset.__name__.lower()
DATASET_METADATA_FILE_NAME = 'prompt.json'


class MathExpressionDatasetTesterService(BaseMathExpressionDatasetTesterService):
    def __init__(
        self,
        dataset_loader_service: BaseDatasetLoaderService,
        math_expression_labeler_assistant: MathExpressionLabelerAssistant,
    ):
        self.dataset_loader_service = dataset_loader_service
        self.math_expression_labeler_assistant = math_expression_labeler_assistant

    async def test(self, test: MathExpressionDatasetTest) -> MathExpressionDatasetTestResult:
        # load dataset
        split_name_to_samples, dataset_metadata_file = self.dataset_loader_service.load(
            dataset_id=test.math_expression_dataset_id,
            dataset_name=DATASET_NAME,
            dataset_metadata_file_name=DATASET_METADATA_FILE_NAME,
            sample_type=MathExpressionSample,
            max_retries=3,
        )
        prompt_collection = LLMPromptCollection.model_validate_json(dataset_metadata_file.content)

        # override assistant
        self.math_expression_labeler_assistant.system_prompt = prompt_collection.system
        self.math_expression_labeler_assistant.user_prompt = prompt_collection.user
        self.math_expression_labeler_assistant.model = test.model
        self.math_expression_labeler_assistant.inference_provider = LLMInferenceProvider(
            test.inference_provider
        )
        self.math_expression_labeler_assistant.model_provider = LLMModelProvider(
            test.model_provider
        )

        # test
        samples = split_name_to_samples[test.math_expression_dataset_split_name]
        inputs: list[MathExpressionLabelerAssistantInput] = []
        input_id_to_math_expression_id: dict[UUID, UUID] = {}

        for sample in samples:
            input = MathExpressionLabelerAssistantInput(latex=sample.katex)
            input_id_to_math_expression_id[input.id] = sample.math_expression_id
            inputs.append(input)

        outputs = await self.math_expression_labeler_assistant.concurrent_assist(inputs)
        labels = [
            MathExpressionLabel(
                math_expression_id=input_id_to_math_expression_id[output.input_id],
                math_expression_dataset_id=test.math_expression_dataset_id,
                index_id=None,
                value=output.label,
            )
            for output in outputs
        ]

        return MathExpressionDatasetTestResult(
            math_expression_dataset_id=test.math_expression_dataset_id,
            math_expression_dataset_test_id=test.id,
            math_expression_labels=labels,
        )
