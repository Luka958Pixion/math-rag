from logging import getLogger
from typing import cast

from label_studio_sdk import Project
from label_studio_sdk.client import AsyncLabelStudio

from math_rag.application.base.services import BaseLabelTaskImporterService
from math_rag.core.types import LabelTaskType


logger = getLogger(__name__)


class LabelStudioTaskImporterService(BaseLabelTaskImporterService):
    def __init__(self, async_label_studio: AsyncLabelStudio):
        self.async_label_studio = async_label_studio

    async def _create_or_update_project(self, title: str, label_config: str) -> Project:
        async_pager = await self.async_label_studio.projects.list()
        project = None

        async for item in async_pager:
            item = cast(Project, item)

            if item.title == title:
                project = item

        if not project:
            create_response = await self.async_label_studio.projects.create(
                title=title, label_config=label_config
            )
            project = await self.async_label_studio.projects.get(create_response.id)
            logger.info(f'Project {create_response.title} created')

        else:
            update_response = await self.async_label_studio.projects.update(
                project.id, label_config=label_config
            )
            logger.info(f'Existing project {update_response.title} updated')

        return project

    async def import_tasks(
        self,
        project_name: str,
        label_config: str,
        tasks: list[LabelTaskType],
    ) -> int:
        request = [task.model_dump() for task in tasks]
        project = await self._create_or_update_project(project_name, label_config)
        response = await self.async_label_studio.projects.import_tasks(project.id, request=request)
        logger.info(f'Imported {response.task_count} tasks into {project.title}')

        return project.id
