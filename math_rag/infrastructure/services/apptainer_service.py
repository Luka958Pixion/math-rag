from asyncio import sleep
from pathlib import Path
from typing import AsyncGenerator

from math_rag.application.base.clients import BaseApptainerClient
from math_rag.application.base.services import BaseApptainerService
from math_rag.application.enums import (
    ApptainerBuildStatus,
    ApptainerOverlayCreateStatus,
)


class ApptainerService(BaseApptainerService):
    def __init__(self, apptainer_client: BaseApptainerClient):
        self.apptainer_client = apptainer_client

    async def build(
        self, def_file_path: Path, *, max_retries: int = 3, poll_interval: float = 5
    ) -> AsyncGenerator[bytes, None]:
        task_id = await self.apptainer_client.build(def_file_path)
        retries = 0

        while True:
            status = await self.apptainer_client.build_status(task_id)

            if status == ApptainerBuildStatus.DONE:
                break

            if status == ApptainerBuildStatus.FAILED:
                if retries < max_retries:
                    task_id = await self.apptainer_client.build(def_file_path)
                    retries += 1

                else:
                    raise Exception('Max retries reached')

            await sleep(poll_interval)

        result = await self.apptainer_client.build_result(task_id)

        return result

    async def overlay_create(
        self, fakeroot: bool, size: int, *, max_retries: int, poll_interval: float
    ) -> AsyncGenerator[bytes, None]:
        task_id = await self.apptainer_client.overlay_create(fakeroot, size)
        retries = 0

        while True:
            status = await self.apptainer_client.overlay_create_status(task_id)

            if status == ApptainerOverlayCreateStatus.DONE:
                break

            if status == ApptainerOverlayCreateStatus.FAILED:
                if retries < max_retries:
                    task_id = await self.apptainer_client.overlay_create(fakeroot, size)
                    retries += 1

                else:
                    raise Exception('Max retries reached')

            await sleep(poll_interval)

        result = await self.apptainer_client.overlay_create_result(task_id)

        return result
