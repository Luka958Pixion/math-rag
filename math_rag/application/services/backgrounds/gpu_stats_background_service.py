from asyncio import sleep

from math_rag.application.base.services import BaseGPUStatsPusherService
from math_rag.application.base.services.backgrounds import BaseBackgroundService
from math_rag.shared.utils import LoggingSuppressorUtil, TypeUtil


POLL_INTERVAL = 1 * 60


class GPUStatsBackgroundService(BaseBackgroundService):
    def __init__(self, gpu_stats_pusher_service: BaseGPUStatsPusherService):
        self.gpu_stats_pusher_service = gpu_stats_pusher_service

    async def start(self):
        logger_type = type(self.gpu_stats_pusher_service)
        logger_name = TypeUtil.get_file_name(logger_type)

        with LoggingSuppressorUtil.suppress(logger_name):
            while True:
                await self.gpu_stats_pusher_service.push()
                await sleep(POLL_INTERVAL)
