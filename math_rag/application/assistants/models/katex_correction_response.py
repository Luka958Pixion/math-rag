from pydantic import BaseModel


class KatexCorrectionResponse(BaseModel):
    katex: str
