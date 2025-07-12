from math_rag.core.models import MathExpression, MathExpressionRelationship

from .base_graph_repository import BaseGraphRepository


class BaseMathExpressionRepository(BaseGraphRepository[MathExpression, MathExpressionRelationship]):
    pass
