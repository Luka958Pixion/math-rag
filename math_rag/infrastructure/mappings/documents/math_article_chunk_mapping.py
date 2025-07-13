from math_rag.core.models import MathArticleChunk
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathArticleChunkDocument


class MathArticleChunkMapping(BaseMapping[MathArticleChunk, MathArticleChunkDocument]):
    @staticmethod
    def to_source(target: MathArticleChunkDocument) -> MathArticleChunk:
        return MathArticleChunk(
            id=target.id,
            math_article_id=target.math_article_id,
            math_expression_index_id=target.math_expression_index_id,
            timestamp=target.timestamp,
            index=target.index,
            indexes=target.indexes,
            text=target.text,
        )

    @staticmethod
    def to_target(source: MathArticleChunk) -> MathArticleChunkDocument:
        return MathArticleChunkDocument(
            id=source.id,
            math_article_id=source.math_article_id,
            math_expression_index_id=source.math_expression_index_id,
            timestamp=source.timestamp,
            index=source.index,
            indexes=source.indexes,
            text=source.text,
        )
