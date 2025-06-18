from logging import getLogger

from label_studio_sdk import Project
from label_studio_sdk.client import AsyncLabelStudio

from math_rag.application.base.services import BaseLabelTaskImporterService
from math_rag.core.types import LabelTaskType


logger = getLogger(__name__)


class LabelStudioTaskImporterService(BaseLabelTaskImporterService):
    def __init__(self, async_label_studio: AsyncLabelStudio):
        self.async_label_studio = async_label_studio

    async def _create_project(
        self, title: str, label_config: str, label_instruction: str | None
    ) -> Project:
        response = await self.async_label_studio.projects.create(
            title=title,
            label_config=label_config,
            expert_instruction=label_instruction,
            show_instruction=label_instruction is not None,
        )
        logger.info(f'Project {response.title} created')

        return await self.async_label_studio.projects.get(response.id)

    async def _update_project(
        self, project_id: int, label_config: str, label_instruction: str | None
    ) -> Project:
        response = await self.async_label_studio.projects.update(
            project_id,
            label_config=label_config,
            expert_instruction=label_instruction,
            show_instruction=label_instruction is not None,
        )
        logger.info(f'Existing project {response.title} updated')

        return await self.async_label_studio.projects.get(response.id)

    async def import_tasks(
        self,
        project_id: int | None,
        *,
        project_name: str,
        label_config: str,
        label_instruction: str | None,
        tasks: list[LabelTaskType],
    ) -> int:
        request = [task.model_dump() for task in tasks]
        project_callback = self._create_project if project_id is None else self._update_project
        project = await project_callback(project_name, label_config, label_instruction)
        response = await self.async_label_studio.projects.import_tasks(project.id, request=request)
        logger.info(f'Imported {response.task_count} tasks into {project.title}')

        return project.id
