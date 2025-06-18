from pydantic import BaseModel


class KatexValidateResult(BaseModel):
    valid: bool
    error: str | None = None
