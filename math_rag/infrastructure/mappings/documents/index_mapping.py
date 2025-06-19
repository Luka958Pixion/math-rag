from math_rag.core.enums import IndexBuildStage
from math_rag.core.models import Index
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import IndexDocument


class IndexMapping(BaseMapping[Index, IndexDocument]):
    @staticmethod
    def to_source(target: IndexDocument) -> Index:
        return Index(
            id=target.id,
            timestamp=target.timestamp,
            build_stage=IndexBuildStage(target.build_stage),
        )

    @staticmethod
    def to_target(source: Index) -> IndexDocument:
        return IndexDocument(
            id=source.id,
            timestamp=source.timestamp,
            build_stage=source.build_stage.value,
        )
