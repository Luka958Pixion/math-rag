from asyncio import sleep

from math_rag.application.base.services import BasePBSProResoucesUsedPusherService
from math_rag.application.base.services.backgrounds import BaseBackgroundService


POLL_INTERVAL = 1 * 60
PBS_JOB_NAME = 'lora'


class PBSProResourcesUsedBackgroundService(BaseBackgroundService):
    def __init__(self, pbs_pro_resources_used_pusher_service: BasePBSProResoucesUsedPusherService):
        self.pbs_pro_resources_used_pusher_service = pbs_pro_resources_used_pusher_service

    async def start(self):
        while True:
            await self.pbs_pro_resources_used_pusher_service.push(PBS_JOB_NAME)
            await sleep(POLL_INTERVAL)
