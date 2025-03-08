from pydantic import BaseModel


class KatexValidationResult(BaseModel):
    valid: bool
    error: str | None = None
