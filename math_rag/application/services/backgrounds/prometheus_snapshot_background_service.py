from asyncio import sleep

from math_rag.application.base.services import BasePrometheusSnapshotLoaderService
from math_rag.application.base.services.backgrounds import BaseBackgroundService


POLL_INTERVAL = 5 * 60


class PrometheusSnapshotBackgroundService(BaseBackgroundService):
    def __init__(self, prometheus_snapshot_loader_service: BasePrometheusSnapshotLoaderService):
        self.prometheus_snapshot_loader_service = prometheus_snapshot_loader_service

    async def start(self):
        while True:
            await self.prometheus_snapshot_loader_service.load()
            await sleep(POLL_INTERVAL)
