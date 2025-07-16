from pathlib import Path

from math_rag.core.enums import MathExpressionIndexBuildStage
from math_rag.core.models import MathExpressionIndex, MathExpressionIndexBuildDetails
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionIndexDocument


class MathExpressionIndexMapping(BaseMapping[MathExpressionIndex, MathExpressionIndexDocument]):
    @staticmethod
    def to_source(target: MathExpressionIndexDocument) -> MathExpressionIndex:
        return MathExpressionIndex(
            id=target.id,
            timestamp=target.timestamp,
            build_stage=MathExpressionIndexBuildStage(target.build_stage),
            build_details=MathExpressionIndexBuildDetails(
                file_path=Path(target.file_path) if target.file_path else None, url=target.url
            ),
        )

    @staticmethod
    def to_target(source: MathExpressionIndex) -> MathExpressionIndexDocument:
        return MathExpressionIndexDocument(
            id=source.id,
            timestamp=source.timestamp,
            build_stage=source.build_stage.value,
            file_path=str(source.build_details.file_path)
            if source.build_details.file_path
            else None,
            url=source.build_details.url,
        )
