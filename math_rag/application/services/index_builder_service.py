from logging import getLogger

from math_rag.application.base.services import BaseIndexBuilderService
from math_rag.core.models import Index


logger = getLogger(__name__)


class IndexBuilderService(BaseIndexBuilderService):
    async def build(index: Index):
        logger.info(f'Starting build for index {index.id}')
        # TODO build
        logger.info(f'Finished build for index {index.id}')
