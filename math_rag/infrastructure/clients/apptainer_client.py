from asyncio import sleep
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
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def build_init(self, def_file_path: Path) -> UUID:
        url = self.base_url + '/apptainer/build'

        with def_file_path.open('rb') as file:
            files = {'def_file': (def_file_path.name, file, 'application/octet-stream')}

            async with AsyncClient() as client:
                response = await client.post(url, files=files)
                result = response.json()
                task_id = UUID(result['task_id'])

                return task_id

    async def build_status(self, task_id: UUID) -> ApptainerBuildStatus:
        url = self.base_url + '/apptainer/build/status'
        payload = {'task_id': str(task_id)}

        async with AsyncClient() as client:
            response = await client.post(url, json=payload)
            result = response.json()
            status = ApptainerBuildStatus(result['status'])

            return status

    async def build_result(self, task_id: UUID) -> AsyncGenerator[bytes, None]:
        url = self.base_url + '/apptainer/build/result'
        payload = {'task_id': str(task_id)}

        async with AsyncClient() as client:
            async with client.stream('POST', url, json=payload) as response:
                response.raise_for_status()

                async for chunk in response.aiter_bytes():
                    yield chunk

    async def build(
        self, def_file_path: Path, *, max_retries: int = 3, poll_interval: float = 5
    ) -> AsyncGenerator[bytes, None]:
        task_id = await self.build_init(def_file_path)
        retries = 0

        while True:
            status = await self.build_status(task_id)

            match status:
                case ApptainerBuildStatus.PENDING | ApptainerBuildStatus.RUNNING:
                    await sleep(poll_interval)

                case ApptainerBuildStatus.DONE:
                    break

                case ApptainerBuildStatus.FAILED:
                    if retries < max_retries:
                        task_id = await self.build_init(def_file_path)
                        retries += 1

                    else:
                        raise Exception('Max retries reached')

        result = await self.build_result(task_id)

        return result

    async def overlay_create_init(self, fakeroot: bool, size: int) -> UUID:
        url = self.base_url + '/overlay/create/build'
        payload = {'fakeroot': fakeroot, 'size': size}

        async with AsyncClient() as client:
            response = await client.post(url, json=payload)
            result = response.json()
            task_id = UUID(result['task_id'])

            return task_id

    async def overlay_create_status(
        self, task_id: UUID
    ) -> ApptainerOverlayCreateStatus:
        url = self.base_url + '/apptainer/overlay/create/status'
        payload = {'task_id': str(task_id)}

        async with AsyncClient() as client:
            response = await client.post(url, json=payload)
            result = response.json()
            status = ApptainerOverlayCreateStatus(result['status'])

            return status

    async def overlay_create_result(self, task_id: UUID) -> AsyncGenerator[bytes, None]:
        url = self.base_url + '/apptainer/overlay/create/result'
        payload = {'task_id': str(task_id)}

        async with AsyncClient() as client:
            async with client.stream('POST', url, json=payload) as response:
                response.raise_for_status()

                async for chunk in response.aiter_bytes():
                    yield chunk

    async def overlay_create(
        self, fakeroot: bool, size: int, *, max_retries: int, poll_interval: float
    ) -> AsyncGenerator[bytes, None]:
        task_id = await self.overlay_create_init(fakeroot, size)
        retries = 0

        while True:
            status = await self.overlay_create_status(task_id)

            match status:
                case (
                    ApptainerOverlayCreateStatus.PENDING
                    | ApptainerOverlayCreateStatus.RUNNING
                ):
                    await sleep(poll_interval)

                case ApptainerOverlayCreateStatus.DONE:
                    break

                case ApptainerOverlayCreateStatus.FAILED:
                    if retries < max_retries:
                        task_id = await self.overlay_create_init(fakeroot, size)
                        retries += 1

                    else:
                        raise Exception('Max retries reached')

        result = await self.overlay_create_result(task_id)

        return result

    async def health(self) -> bool:
        url = self.base_url + '/health'

        async with AsyncClient() as client:
            response = await client.get(url)
            result = response.json()

            return result['status'] == 'ok'
