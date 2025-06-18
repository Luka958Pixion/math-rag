from asyncio import sleep
from io import BytesIO

from label_studio_sdk.client import AsyncLabelStudio
from pydantic import TypeAdapter

from math_rag.infrastructure.models.labels import Task


class LabelStudioTaskExporterService:
    def __init__(self, async_label_studio: AsyncLabelStudio):
        self.async_label_studio = async_label_studio

    async def export_tasks(self, project_id: int) -> list[Task]:
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
        type_adapter = TypeAdapter(list[Task])

        return type_adapter.validate_json(content)
