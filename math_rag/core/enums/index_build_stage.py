from enum import Enum


class IndexBuildStage(str, Enum):
    LOADED_MATH_ARTICLES = 'loaded_math_articles'
    LOADED_MATH_EXPRESSIONS = 'loaded_math_expressions'
    LOADED_MATH_EXPRESSION_LABELS = 'loaded_math_expression_labels'
