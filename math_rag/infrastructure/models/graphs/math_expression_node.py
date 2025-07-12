from neomodel import (
    AsyncRelationshipTo,
    AsyncStructuredNode,
    AsyncZeroOrMore,
    BooleanProperty,
    DateTimeProperty,
    IntegerProperty,
    StringProperty,
    UniqueIdProperty,
)

from .math_expression_rel import MathExpressionRel


class MathExpressionNode(AsyncStructuredNode):
    uid = UniqueIdProperty()
    math_article_id = StringProperty(required=True)
    math_expression_group_id = StringProperty(required=False)
    math_expression_index_id = StringProperty(required=False)
    math_expression_dataset_id = StringProperty(required=False)
    timestamp = DateTimeProperty(required=True)
    latex = StringProperty(required=True)
    katex = StringProperty(required=False)
    position = IntegerProperty(required=True)
    is_inline = BooleanProperty(required=True)
    related_to = AsyncRelationshipTo(
        cls_name='MathExpressionNode',
        relation_type='RELATED_TO',
        cardinality=AsyncZeroOrMore,
        model=MathExpressionRel,
    )
