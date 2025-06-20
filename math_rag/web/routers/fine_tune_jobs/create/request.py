from pydantic import BaseModel


class Request(BaseModel):
    provider_name: str
    model_name: str
