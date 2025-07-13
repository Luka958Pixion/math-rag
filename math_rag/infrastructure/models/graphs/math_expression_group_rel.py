from neomodel import (
    AsyncStructuredRel,
    DateTimeProperty,
    StringProperty,
    UniqueIdProperty,
)


class MathExpressionGroupRel(AsyncStructuredRel):
    uid = UniqueIdProperty()
    math_expression_index_id = StringProperty(required=True)
    math_expression_id = StringProperty(required=True)
    math_expression_group_id = StringProperty(required=True)
    timestamp = DateTimeProperty(required=True)
