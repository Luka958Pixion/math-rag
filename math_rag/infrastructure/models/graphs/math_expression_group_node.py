from neomodel import (
    AsyncRelationshipFrom,
    AsyncStructuredNode,
    AsyncZeroOrMore,
    DateTimeProperty,
    StringProperty,
    UniqueIdProperty,
)

from .math_expression_group_rel import MathExpressionGroupRel


class MathExpressionGroupNode(AsyncStructuredNode):
    uid = UniqueIdProperty()
    math_expression_index_id = StringProperty(required=False)
    timestamp = DateTimeProperty(required=True)
    member_of = AsyncRelationshipFrom(
        cls_name='.math_expression_node.MathExpressionNode',
        relation_type='MEMBER_OF',
        cardinality=AsyncZeroOrMore,
        model=MathExpressionGroupRel,
    )
