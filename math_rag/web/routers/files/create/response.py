from pydantic import BaseModel


class Response(BaseModel):
    token: str
