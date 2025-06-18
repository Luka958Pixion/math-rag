from math_rag.application.base.services import (
    BaseLabelTaskExporterService,
    BaseMathExpressionLabelExporterService,
)
from math_rag.core.enums import MathExpressionLabelEnum
from math_rag.core.models import MathExpressionLabel, MathExpressionLabelTask


class MathExpressionLabelExporterService(BaseMathExpressionLabelExporterService):
    def __init__(self, label_exporter_service: BaseLabelTaskExporterService):
        self.label_exporter_service = label_exporter_service

    async def export(self, project_id: int) -> list[MathExpressionLabel]:
        label_task_to_label_value = await self.label_exporter_service.export_tasks(
            project_id, label_task_type=MathExpressionLabelTask
        )

        return [
            MathExpressionLabel(
                id=label_task.id,
                math_expression_id=label_task.math_expression_id,
                math_expression_dataset_id=label_task.math_expression_dataset_id,
                timestamp=label_task.timestamp,
                value=MathExpressionLabelEnum(label_value),
            )
            for label_task, label_value in label_task_to_label_value.items()
        ]
