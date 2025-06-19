from math_rag.core.models import MathExpressionDatasetTest
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDatasetTestDocument


class MathExpressionDatasetTestMapping(
    BaseMapping[MathExpressionDatasetTest, MathExpressionDatasetTestDocument]
):
    @staticmethod
    def to_source(target: MathExpressionDatasetTestDocument) -> MathExpressionDatasetTest:
        return MathExpressionDatasetTest(
            id=target.id,
            math_expression_dataset_id=target.math_expression_dataset_id,
            math_expression_dataset_split_name=target.math_expression_dataset_split_name,
            timestamp=target.timestamp,
            inference_provider=target.inference_provider,
            model_provider=target.model_provider,
            model=target.model,
        )

    @staticmethod
    def to_target(source: MathExpressionDatasetTest) -> MathExpressionDatasetTestDocument:
        return MathExpressionDatasetTestDocument(
            id=source.id,
            math_expression_dataset_id=source.math_expression_dataset_id,
            math_expression_dataset_split_name=source.math_expression_dataset_split_name,
            timestamp=source.timestamp,
            inference_provider=source.inference_provider,
            model_provider=source.model_provider,
            model=source.model,
        )
