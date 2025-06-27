from asyncio import sleep

from math_rag.application.base.services import BaseGPUStatsPusherService
from math_rag.application.base.services.backgrounds import BaseBackgroundService


POLL_INTERVAL = 1 * 60


class GPUStatsBackgroundService(BaseBackgroundService):
    def __init__(self, gpu_stats_pusher_service: BaseGPUStatsPusherService):
        self.gpu_stats_pusher_service = gpu_stats_pusher_service

    async def start(self):
        while True:
            await self.gpu_stats_pusher_service.push()
            await sleep(POLL_INTERVAL)
