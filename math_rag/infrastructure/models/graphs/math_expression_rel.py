from neomodel import AsyncStructuredRel, DateTimeProperty, StringProperty, UniqueIdProperty


class MathExpressionRel(AsyncStructuredRel):
    uid = UniqueIdProperty()
    math_expression_index_id = StringProperty(required=True)
    math_expression_source_id = StringProperty(required=True)
    math_expression_target_id = StringProperty(required=True)
    timestamp = DateTimeProperty(required=True)
