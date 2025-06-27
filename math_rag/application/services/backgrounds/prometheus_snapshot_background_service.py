from asyncio import sleep

from math_rag.application.base.services import BasePrometheusSnapshotLoaderService
from math_rag.application.base.services.backgrounds import BaseBackgroundService
from math_rag.shared.utils import LoggingSuppressorUtil, TypeUtil


POLL_INTERVAL = 5 * 60


class PrometheusSnapshotBackgroundService(BaseBackgroundService):
    def __init__(self, prometheus_snapshot_loader_service: BasePrometheusSnapshotLoaderService):
        self.prometheus_snapshot_loader_service = prometheus_snapshot_loader_service

    async def start(self):
        logger_type = type(self.prometheus_snapshot_loader_service)
        logger_name = TypeUtil.get_file_name(logger_type)

        with LoggingSuppressorUtil.suppress(logger_name):
            while True:
                await self.prometheus_snapshot_loader_service.load()
                await sleep(POLL_INTERVAL)
