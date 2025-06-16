from pydantic import BaseModel


class KatexRenderResult(BaseModel):
    html: str | None = None
    error: str | None = None
