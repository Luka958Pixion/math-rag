from logging import getLogger

from math_rag.application.assistants.prompts import MATH_EXPRESSION_LABELER_PROMPT_COLLECTION
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

FIELDS = ['latex', 'label']


class MathExpressionDatasetPublisherService(BaseMathExpressionDatasetPublisherService):
    def __init__(
        self,
        math_expression_sample_repository: BaseMathExpressionSampleRepository,
        dataset_publisher_service: BaseDatasetPublisherService,
    ):
        self.math_expression_sample_repository = math_expression_sample_repository
        self.dataset_publisher_service = dataset_publisher_service

    async def publish(self, dataset: MathExpressionDataset):
        math_expression_samples = [
            math_expression_sample
            async for batch in self.math_expression_sample_repository.batch_find_many(
                dataset.build_from_id if dataset.build_from_id else dataset.id, batch_size=1000
            )
            for math_expression_sample in batch
        ]

        fields = [field for field in MathExpressionSample.model_fields]
        json_str = MATH_EXPRESSION_LABELER_PROMPT_COLLECTION.model_dump_json(indent=4)
        content = json_str.encode('utf-8')
        dataset_metadata_file = DatasetMetadataFile(name='prompt.json', content=content)

        self.dataset_publisher_service.publish(
            dataset_id=dataset.id,
            dataset_name=dataset.__class__.__name__.lower(),
            samples=math_expression_samples,
            sample_type=MathExpressionSample,
            fields=fields,
            dataset_splits=dataset.build_details.splits,
            dataset_metadata_file=dataset_metadata_file,
        )

        logger.info(
            f'{self.__class__.__name__} published '
            f'{len(math_expression_samples)} math expression samples'
        )
