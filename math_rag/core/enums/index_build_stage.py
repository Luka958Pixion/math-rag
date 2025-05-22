from enum import Enum


class IndexBuildStage(str, Enum):
    LOADING_MATH_ARTICLES = 'loading_math_articles'
    LOADING_MATH_EXPRESSIONS = 'loading_math_expressions'
    LOADING_MATH_EXPRESSION_LABELS = 'loading_math_expression_labels'
