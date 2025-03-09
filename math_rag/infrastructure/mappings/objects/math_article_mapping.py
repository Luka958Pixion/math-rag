from uuid import UUID

from math_rag.core.models import MathArticle
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.objects import MathArticleObject


class MathArticleMapping(BaseMapping[MathArticle, MathArticleObject]):
    @staticmethod
    def to_source(target: MathArticleObject) -> MathArticle:
        math_article = MathArticle(
            id=UUID(target.id),
            name=target.name,
            bytes=target.bytes,
        )

        return math_article

    @staticmethod
    def to_target(source: MathArticle) -> MathArticleObject:
        math_article_object = MathArticleObject(
            id=str(source.id),
            name=source.name,
            bytes=source.bytes,
        )

        return math_article_object
