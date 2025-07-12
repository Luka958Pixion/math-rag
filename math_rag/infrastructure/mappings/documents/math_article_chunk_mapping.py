from math_rag.core.models import MathArticleChunk
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathArticleChunkDocument


class MathArticleChunkMapping(BaseMapping[MathArticleChunk, MathArticleChunkDocument]):
    @staticmethod
    def to_source(target: MathArticleChunkDocument) -> MathArticleChunk:
        return MathArticleChunk.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: MathArticleChunk) -> MathArticleChunkDocument:
        return MathArticleChunkDocument.model_validate(source.model_dump())
