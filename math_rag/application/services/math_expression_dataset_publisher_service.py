from logging import getLogger

from math_rag.application.assistants.prompts import MATH_EXPRESSION_LABELER_PROMPT
from math_rag.application.base.repositories.documents import (
    BaseMathExpressionLabelRepository,
)
from math_rag.application.base.services import BaseDatasetPublisherService
from math_rag.application.models.datasets import (
    DatasetMetadataFile,
    DatasetSplitSettings,
    MathExpressionDataset,
    MathExpressionSample,
)


logger = getLogger(__name__)


class MathExpressionDatasetPublisherService:
    def __init__(
        self,
        math_expression_label_repository: BaseMathExpressionLabelRepository,
        dataset_publisher_service: BaseDatasetPublisherService,
    ):
        self.math_expression_label_repository = math_expression_label_repository
        self.dataset_publisher_service = dataset_publisher_service

    async def publish(self):
        math_expression_samples: list[MathExpressionSample] = []

        async for (
            math_expression_label_batch
        ) in self.math_expression_label_repository.batch_find_many(batch_size=1000):
            math_expression_sample_batch = [
                MathExpressionSample(
                    latex=math_expression_label.latex,  # TODO
                    label=math_expression_label.value,
                )
                for math_expression_label in math_expression_label_batch
            ]
            math_expression_samples.extend(math_expression_sample_batch)

        math_expression_dataset = MathExpressionDataset(math_expression_samples)
        dataset_split_settings = DatasetSplitSettings(
            train_ratio=0.8, validate_ratio=0.1, test_ratio=0.1, seed=42
        )

        json_str = MATH_EXPRESSION_LABELER_PROMPT.model_dump_json(indent=4)
        content = json_str.encode('utf-8')
        dataset_metadata_file = DatasetMetadataFile(name='prompt.json', content=content)

        self.dataset_publisher_service.publish(
            math_expression_dataset,
            MathExpressionSample,
            dataset_split_settings,
            dataset_metadata_file,
        )

        logger.info(
            f'{self.__class__.__name__} published {len(math_expression_samples)} math expression samples'
        )
