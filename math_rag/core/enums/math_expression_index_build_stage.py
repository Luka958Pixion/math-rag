from enum import Enum


class MathExpressionIndexBuildStage(str, Enum):
    LOAD_MATH_ARTICLES = 'load_math_articles'
    LOAD_MATH_EXPRESSIONS = 'load_math_expressions'
    LOAD_MATH_EXPRESSION_LABELS = 'load_math_expression_labels'
    LOAD_MATH_EXPRESSION_CONTEXTS = 'load_math_expression_contexts'
    LOAD_MATH_EXPRESSION_DESCRIPTIONS = 'load_math_expression_descriptions'
    LOAD_MATH_EXPRESSION_DESCRIPTION_OPTS = 'load_math_expression_description_opts'
    LOAD_MATH_EXPRESSION_GROUPS = 'load_math_expression_groups'
    LOAD_MATH_EXPRESSION_GROUP_RELATIONSHIPS = 'load_math_expression_group_relationships'
    LOAD_MATH_ARTICLE_CHUNKS = 'load_math_article_chunks'
    LOAD_MATH_EXPRESSION_RELATIONSHIPS = 'load_math_expression_relationships'
    LOAD_MATH_EXPRESSION_RELATIONSHIP_DESCRIPTIONS = (
        'load_math_expression_relationship_descriptions'
    )
