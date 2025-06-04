from pydantic import BaseModel


class LatexMathNode(BaseModel):
    latex: str
    position: int
    is_inline: bool
