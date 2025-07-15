from abc import abstractmethod
from typing import Callable
from uuid import UUID

from math_rag.core.models import MathExpression, MathExpressionRelationship

from .base_graph_repository import BaseGraphRepository


class BaseMathExpressionRepository(BaseGraphRepository[MathExpression, MathExpressionRelationship]):
    @abstractmethod
    async def breadth_first_search(
        self, start_id: UUID, *, max_depth: int, filter_cb: Callable[[MathExpression], bool] | None
    ) -> list[tuple[UUID, UUID, UUID]]:
        pass
