from enum import Enum


class MathExpressionDatasetBuildStage(str, Enum):
    LOAD_MATH_ARTICLES = 'load_math_articles'
    LOAD_MATH_EXPRESSIONS = 'load_math_expressions'
    LOAD_MATH_EXPRESSION_LABELS = 'load_math_expression_labels'
    LOAD_MATH_EXPRESSION_SAMPLES = 'load_math_expression_samples'
