from asyncio import sleep

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionIndexRepository,
    BaseTaskRepository,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.core.enums import TaskStatus
from math_rag.core.models import MathExpressionIndex, MathExpressionIndexBuildDetails, Task
from math_rag.mcp.base import BaseTool


POLL_INTERVAL = 15


class IndexerToolResult(BaseModel):
    index_id: str


class IndexerTool(BaseTool):
    async def index(
        self,
        url: str,
    ) -> IndexerToolResult:
        return await self._index(url)

    @inject
    async def _index(
        self,
        url: str,
        index_repository: BaseMathExpressionIndexRepository = Depends(
            Provide[ApplicationContainer.math_expression_index_repository]
        ),
        task_repository: BaseTaskRepository = Depends(
            Provide[ApplicationContainer.task_repository]
        ),
    ) -> IndexerToolResult:
        # prepare task
        index_build_details = MathExpressionIndexBuildDetails(file_path=None, url=url)
        index = MathExpressionIndex(build_details=index_build_details)
        task = Task(model_id=index.id, model_name=MathExpressionIndex.__name__)

        await index_repository.insert_one(index)
        await task_repository.insert_one(task)

        # wait for task to end
        while True:
            if task.task_status == TaskStatus.FINISHED:
                return IndexerToolResult(index_id=str(index.id))

            if task.task_status == TaskStatus.FAILED:
                raise HTTPException(f'Creating an index for URL `{url}` failed')

            await sleep(POLL_INTERVAL)

            task = await task_repository.find_one(filter=dict(id=task.id))
            if not task:
                raise ValueError()

    def add(self, mcp: FastMCP):
        mcp.add_tool(
            self.index,
            name=self.__class__.__name__,
            description=(
                'Builds an index of math literature from the provided URL. '
                'A required step before solving any math problems. '
                'Returns a UUID of the created index.'
            ),
            annotations=ToolAnnotations(title='MathRAG Literature Indexer'),
        )
