from pydantic import BaseModel


class KatexRenderSvgResult(BaseModel):
    svg: str | None = None
    error: str | None = None
