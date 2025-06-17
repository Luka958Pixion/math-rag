import re

from logging import getLogger
from typing import cast
from uuid import UUID

from label_studio_sdk import Project
from label_studio_sdk.client import AsyncLabelStudio
from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk.label_interface.create import choices

from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.base.services import BaseDatasetLoaderService
from math_rag.core.types import SampleType


logger = getLogger(__name__)


class LabelStudioPublisherService:
    def __init__(
        self,
        async_label_studio: AsyncLabelStudio,
        dataset_loader_service: BaseDatasetLoaderService,
        katex_client: BaseKatexClient,
    ):
        self.async_label_studio = async_label_studio
        self.dataset_loader_service = dataset_loader_service
        self.katex_client = katex_client

    def text_to_html(text: str) -> str:
        """
        Convert any multiline string into HTML by:
        - Wrapping non-numbered lines in <p>...</p>
        - Grouping contiguous lines starting with '1.', '2.', etc. into <ol><li>...</li></ol>
        """
        html_lines = []
        in_list = False

        for line in text.splitlines():
            if re.match(r'^\s*\d+\.', line):
                if not in_list:
                    html_lines.append('<ol>')
                    in_list = True

                html_lines.append(f'  <li>{line}</li>')

            else:
                if in_list:
                    html_lines.append('</ol>')
                    in_list = False

                html_lines.append(f'<p>{line}</p>')

        if in_list:
            html_lines.append('</ol>')

        return '\n'.join(html_lines)

    async def publish(
        self,
        dataset_id: UUID,
        dataset_name: str,
        split_name: str,
        sample_type: type[SampleType],
    ) -> int:
        split_name_to_samples, _ = self.dataset_loader_service.load(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            dataset_metadata_file_name=None,
            sample_type=sample_type,
            max_retries=3,
        )
        samples = split_name_to_samples[split_name]

        async_pager = await self.async_label_studio.projects.list()

        project_title = dataset_name
        project = None

        async for item in async_pager:
            item = cast(Project, item)

            if item.title == project_title:
                project = item

        labels = [label.value for label in x]

        label_config = LabelInterface.create(
            {  # TODO
                'html': 'HyperText',
                'latex': 'Text',
                'label': choices(labels),
            }
        )

        if not project:
            project = await self.async_label_studio.projects.create(
                title=project_title, label_config=label_config
            )
            logger.info(f'Project {project.title} created')

        else:
            update_response = await self.async_label_studio.projects.update(
                project.id, label_config=label_config
            )
            logger.info(f'Existing project {update_response.title} updated')

        katexes = [sample.latex.strip('$') for sample in samples]  # TODO
        katex_render_results = await self.katex_client.batch_render_many(katexes, batch_size=50)

        # TODO check for errors

        tasks = [
            dict(**sample.model_dump(), html=katex_render_result.html)
            for sample, katex_render_result in zip(samples, katex_render_results)
        ]

        import_tasks_response = await self.async_label_studio.projects.import_tasks(
            id=project.id, request=tasks
        )
        logger.info(f'Imported {import_tasks_response.task_count} tasks into {project.title}')

        return project.id
