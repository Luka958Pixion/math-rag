from math_rag.core.enums import IndexBuildStage, IndexBuildStatus
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
            build_status=IndexBuildStatus(target.build_status),
            build_from_index_id=target.build_from_index_id,
            build_from_stage=IndexBuildStage(target.build_from_stage)
            if target.build_from_stage
            else None,
        )

    @staticmethod
    def to_target(source: Index) -> IndexDocument:
        return IndexDocument(
            id=source.id,
            timestamp=source.timestamp,
            build_stage=source.build_stage.value,
            build_status=source.build_status.value,
            build_from_index_id=source.build_from_index_id,
            build_from_stage=source.build_from_stage.value
            if source.build_from_stage
            else None,
        )
