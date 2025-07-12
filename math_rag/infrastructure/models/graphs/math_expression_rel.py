from neomodel import (
    AsyncStructuredRel,
    DateTimeProperty,
    IntegerProperty,
    StringProperty,
    UniqueIdProperty,
)


class MathExpressionRel(AsyncStructuredRel):
    uid = UniqueIdProperty()
    math_article_chunk_id = StringProperty(required=True)
    math_expression_index_id = StringProperty(required=True)
    math_expression_source_id = StringProperty(required=True)
    math_expression_target_id = StringProperty(required=True)
    math_expression_source_index = IntegerProperty(required=True)
    math_expression_target_index = IntegerProperty(required=True)
    timestamp = DateTimeProperty(required=True)
