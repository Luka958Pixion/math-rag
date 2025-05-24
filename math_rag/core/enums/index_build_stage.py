from enum import Enum


class IndexBuildStage(str, Enum):
    LOAD_MATH_ARTICLES = 'load_math_articles'
    LOAD_MATH_EXPRESSIONS = 'load_math_expressions'
    LOAD_MATH_EXPRESSION_LABELS = 'load_math_expression_labels'
