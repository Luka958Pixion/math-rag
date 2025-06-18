from abc import ABC, abstractmethod

from math_rag.core.models import MathExpressionLabel


class BaseMathExpressionLabelExporterService(ABC):
    @abstractmethod
    async def export(self, project_id: int) -> list[MathExpressionLabel]:
        pass
