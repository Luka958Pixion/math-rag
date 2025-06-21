from math_rag.core.models import MathExpressionDatasetTestResult
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDatasetTestResultDocument

from .math_expression_label_mapping import MathExpressionLabelMapping


class MathExpressionDatasetTestResultMapping(
    BaseMapping[MathExpressionDatasetTestResult, MathExpressionDatasetTestResultDocument]
):
    @staticmethod
    def to_source(
        target: MathExpressionDatasetTestResultDocument,
    ) -> MathExpressionDatasetTestResult:
        return MathExpressionDatasetTestResult(
            id=target.id,
            math_expression_dataset_id=target.math_expression_dataset_id,
            math_expression_dataset_split_name=target.math_expression_dataset_split_name,
            math_expression_dataset_test_id=target.math_expression_dataset_test_id,
            math_expression_labels=[
                MathExpressionLabelMapping.to_source(math_expression_label)
                for math_expression_label in target.math_expression_labels
            ],
            timestamp=target.timestamp,
        )

    @staticmethod
    def to_target(
        source: MathExpressionDatasetTestResult,
    ) -> MathExpressionDatasetTestResultDocument:
        return MathExpressionDatasetTestResultDocument(
            id=source.id,
            math_expression_dataset_id=source.math_expression_dataset_id,
            math_expression_dataset_split_name=source.math_expression_dataset_split_name,
            math_expression_dataset_test_id=source.math_expression_dataset_test_id,
            math_expression_labels=[
                MathExpressionLabelMapping.to_target(math_expression_label)
                for math_expression_label in source.math_expression_labels
            ],
            timestamp=source.timestamp,
        )
