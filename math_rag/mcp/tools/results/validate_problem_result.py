from pydantic import BaseModel


class ValidateProblemResult(BaseModel):
    message: str
