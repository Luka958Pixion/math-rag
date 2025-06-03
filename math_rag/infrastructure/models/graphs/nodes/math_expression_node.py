from neomodel import AsyncRelationshipTo, AsyncStructuredNode, AsyncZeroOrMore, UniqueIdProperty

from math_rag.infrastructure.models.graphs.rels import AppliesToRel


class MathExpressionNode(AsyncStructuredNode):
    uid = UniqueIdProperty(required=True)
    applies_to = AsyncRelationshipTo(
        cls_name='MathExpression',
        relation_type=AppliesToRel.__name__.removesuffix('Rel').upper(),
        cardinality=AsyncZeroOrMore,
        model=AppliesToRel,
    )
