from pydantic import BaseModel


class MathArticleObject(BaseModel):
    id: str
    name: str
    bytes: bytes
