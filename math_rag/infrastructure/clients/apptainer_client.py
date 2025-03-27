from pathlib import Path
from typing import AsyncGenerator
from uuid import UUID

from httpx import AsyncClient

from math_rag.application.base.clients import BaseApptainerClient
from math_rag.application.enums import (
    ApptainerBuildStatus,
    ApptainerOverlayCreateStatus,
)


class ApptainerClient(BaseApptainerClient):
    async def build(self, def_file_path: Path) -> UUID:
        url = 'http://localhost:7015/apptainer/build'

        with def_file_path.open('rb') as file:
            files = {'def_file': (def_file_path.name, file, 'application/octet-stream')}

            async with AsyncClient() as client:
                response = await client.post(url, files=files)
                result = response.json()
                task_id = UUID(result['task_id'])

                return task_id

    async def build_status(self, task_id: UUID) -> ApptainerBuildStatus:
        url = 'http://localhost:7015/apptainer/build/status'
        payload = {'task_id': str(task_id)}

        async with AsyncClient() as client:
            response = await client.post(url, json=payload)
            result = response.json()
            status = ApptainerBuildStatus(result['status'])

            return status

    async def build_result(self, task_id: UUID) -> AsyncGenerator[bytes, None]:
        url = 'http://localhost:7015/apptainer/build/result'
        payload = {'task_id': str(task_id)}

        async with AsyncClient() as client:
            async with client.stream('POST', url, json=payload) as response:
                response.raise_for_status()

                async for chunk in response.aiter_bytes():
                    yield chunk

    async def overlay_create(self, fakeroot: bool, size: int) -> UUID:
        url = 'http://localhost:7015/overlay/create/build'
        payload = {'fakeroot': fakeroot, 'size': size}

        async with AsyncClient() as client:
            response = await client.post(url, json=payload)
            result = response.json()
            task_id = UUID(result['task_id'])

            return task_id

    async def overlay_create_status(
        self, task_id: UUID
    ) -> ApptainerOverlayCreateStatus:
        url = 'http://localhost:7015/apptainer/overlay/create/status'
        payload = {'task_id': str(task_id)}

        async with AsyncClient() as client:
            response = await client.post(url, json=payload)
            result = response.json()
            status = ApptainerOverlayCreateStatus(result['status'])

            return status

    async def overlay_create_result(self, task_id: UUID) -> AsyncGenerator[bytes, None]:
        url = 'http://localhost:7015/apptainer/overlay/create/result'
        payload = {'task_id': str(task_id)}

        async with AsyncClient() as client:
            async with client.stream('POST', url, json=payload) as response:
                response.raise_for_status()

                async for chunk in response.aiter_bytes():
                    yield chunk
