from uuid import UUID

from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.base.services import (
    BaseDatasetLoaderService,
    BaseLabelConfigBuilderService,
    BaseLabelTaskImporterService,
    BaseMathExpressionLabelTaskImporterService,
)
from math_rag.core.enums import MathExpressionLabelEnum
from math_rag.core.models import (
    MathExpressionDataset,
    MathExpressionLabelTask,
    MathExpressionSample,
)


class MathExpressionLabelTaskImporterService(BaseMathExpressionLabelTaskImporterService):
    def __init__(
        self,
        dataset_loader_service: BaseDatasetLoaderService,
        katex_client: BaseKatexClient,
        label_config_builder_service: BaseLabelConfigBuilderService,
        label_task_importer_service: BaseLabelTaskImporterService,
    ):
        self.dataset_loader_service = dataset_loader_service
        self.katex_client = katex_client
        self.label_config_builder_service = label_config_builder_service
        self.label_task_importer_service = label_task_importer_service

    async def import_tasks(
        self, project_id: int | None, *, dataset_id: UUID, split_name: str
    ) -> int:
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

        katexes = [sample.katex.strip('$') for sample in samples]
        katex_render_results = await self.katex_client.batch_render_many(katexes, batch_size=50)

        for katex_render_result in katex_render_results:
            if katex_render_result.error:
                raise ValueError(f'KaTeX rendering failed with {katex_render_result.error}')

        tasks = [
            MathExpressionLabelTask(
                math_expression_id=sample.math_expression_id,
                math_expression_dataset_id=sample.math_expression_dataset_id,
                timestamp=sample.timestamp,
                katex=sample.katex,
                html=katex_render_result.html,
            )
            for sample, katex_render_result in zip(samples, katex_render_results)
        ]

        field_name_to_tag_type = {
            'html': 'hyper_text',
            'katex': 'text',
            'label': 'choices',
        }

        label_config = self.label_config_builder_service.build(field_name_to_tag_type, label_names)

        return await self.label_task_importer_service.import_tasks(
            project_id, project_name=project_name, label_config=label_config, tasks=tasks
        )
