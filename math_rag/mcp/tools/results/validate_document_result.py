from pydantic import BaseModel


class ValidateDocumentResult(BaseModel):
    message: str
