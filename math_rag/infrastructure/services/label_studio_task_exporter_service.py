from asyncio import sleep
from io import BytesIO

from label_studio_sdk.client import AsyncLabelStudio
from pydantic import TypeAdapter

from math_rag.application.base.services import BaseLabelTaskExporterService
from math_rag.core.types import LabelTaskType
from math_rag.infrastructure.models.labels import Task


class LabelStudioTaskExporterService(BaseLabelTaskExporterService):
    def __init__(self, async_label_studio: AsyncLabelStudio):
        self.async_label_studio = async_label_studio

    async def export_tasks(
        self, project_id: int, *, label_task_type: type[LabelTaskType]
    ) -> dict[LabelTaskType, str]:
        export_snapshot = await self.async_label_studio.projects.exports.create(project_id)
        export = await self.async_label_studio.projects.exports.get(project_id, export_snapshot.id)

        while True:
            match export.status:
                case 'created' | 'in_progress':
                    sleep(15)

                case 'failed':
                    raise ValueError('Snapshot export failed')

                case 'completed':
                    break

        buffer = BytesIO()

        async for chunk in self.async_label_studio.projects.exports.download(
            project_id, export_snapshot.id, export_type='JSON'
        ):
            buffer.write(chunk)

        buffer.seek(0)
        content = buffer.read().decode('utf-8')
        type_adapter = TypeAdapter(list[Task[label_task_type]])
        tasks = type_adapter.validate_json(content)

        label_task_to_label_value = {}

        for task in tasks:
            # suppose choices always have one element
            label_values = [
                result.value.choices[0]
                for annotation in task.annotations
                for result in annotation.result
            ]

            if not label_values:
                raise ValueError()

            # majority voting
            label_value = max(set(label_values), key=label_values.count)
            label_task_to_label_value[task.data] = label_value

        return label_task_to_label_value
