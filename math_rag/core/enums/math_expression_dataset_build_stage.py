from math_rag.core.base import BaseDatasetBuildStage


class MathExpressionDatasetBuildStage(BaseDatasetBuildStage):
    LOAD_MATH_ARTICLES = 'load_math_articles'
    LOAD_MATH_EXPRESSIONS = 'load_math_expressions'
    LOAD_MATH_EXPRESSION_LABELS = 'load_math_expression_labels'

    @classmethod
    def default(cls):
        return cls.LOAD_MATH_ARTICLES
