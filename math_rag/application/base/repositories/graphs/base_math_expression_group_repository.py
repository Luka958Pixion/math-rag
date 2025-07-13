from math_rag.core.models import MathExpressionGroup, MathExpressionGroupRelationship

from .base_graph_repository import BaseGraphRepository


class BaseMathExpressionGroupRepository(
    BaseGraphRepository[MathExpressionGroup, MathExpressionGroupRelationship]
):
    pass
