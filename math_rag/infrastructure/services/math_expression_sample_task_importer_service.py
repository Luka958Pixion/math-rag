from uuid import UUID

from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.base.services import (
    BaseDatasetLoaderService,
    BaseLabelTaskImporterService,
)
from math_rag.core.enums import MathExpressionLabelEnum
from math_rag.core.models import (
    MathExpressionDataset,
    MathExpressionLabelTask,
    MathExpressionSample,
)
from math_rag.infrastructure.utils import LabelConfigBuilderUtil


class MathExpressionSampleTaskImporterService:
    def __init__(
        self,
        dataset_loader_service: BaseDatasetLoaderService,
        katex_client: BaseKatexClient,
        label_task_importer_service: BaseLabelTaskImporterService,
    ):
        self.dataset_loader_service = dataset_loader_service
        self.katex_client = katex_client
        self.label_task_importer_service = label_task_importer_service

    async def import_tasks(self, dataset_id: UUID, split_name: str):
        dataset_name = MathExpressionDataset.__name__.lower()
        project_name = MathExpressionLabelTask.__name__.lower()
        label_names = [label.value for label in MathExpressionLabelEnum]

        split_name_to_samples, _ = self.dataset_loader_service.load(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            dataset_metadata_file_name=None,
            sample_type=MathExpressionSample,
            max_retries=3,
        )
        samples = split_name_to_samples[split_name]

        katexes = [sample.latex.strip('$') for sample in samples]  # TODO
        katex_render_results = await self.katex_client.batch_render_many(katexes, batch_size=50)
        # TODO validate before render (use katex when creating sample!)

        # TODO check for errors
        # TODO create MathExpressionLabelTask

        tasks = [
            dict(**sample.model_dump(), html=katex_render_result.html)
            for sample, katex_render_result in zip(samples, katex_render_results)
        ]

        field_name_to_tag_type = ...

        label_config = LabelConfigBuilderUtil.build(field_name_to_tag_type, label_names)

        return await self.label_task_importer_service.import_tasks(
            project_name, label_config, tasks
        )
