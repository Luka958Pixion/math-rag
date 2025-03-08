from uuid import UUID

from pydantic import BaseModel

from math_rag.core.models import MathArticle


class MathArticleObject(BaseModel):
    id: str
    name: str
    bytes: bytes

    @classmethod
    def from_internal(cls, inter: MathArticle) -> 'MathArticleObject':
        return cls(
            _id=str(inter.id),
            name=inter.name,
            bytes=inter.bytes,
        )

    @classmethod
    def to_internal(cls, obj: 'MathArticleObject') -> MathArticle:
        return cls(
            id=UUID(obj.id),
            name=obj.name,
            bytes=obj.bytes,
        )
