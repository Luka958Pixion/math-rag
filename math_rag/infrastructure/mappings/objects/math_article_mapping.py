from uuid import UUID

from math_rag.core.models import MathArticle
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.objects import MathArticleObject


class MathArticleMapping(BaseMapping[MathArticle, MathArticleObject]):
    @classmethod
    def to_source(cls, target: MathArticleObject) -> MathArticle:
        return cls(
            id=UUID(target.id),
            name=target.name,
            bytes=target.bytes,
        )

    @classmethod
    def to_target(cls, source: MathArticle) -> MathArticleObject:
        return cls(
            id=str(source.id),
            name=source.name,
            bytes=source.bytes,
        )
