from neomodel import AsyncRelationshipTo, AsyncStructuredNode, UniqueIdProperty

from math_rag.infrastructure.models.graphs.rels import AppliesToRel


class MathExpressionNode(AsyncStructuredNode):
    id = UniqueIdProperty(required=True)
    applies_to = AsyncRelationshipTo(
        'MathExpression', AppliesToRel.__name__.removesuffix('Rel').upper(), model=AppliesToRel
    )
