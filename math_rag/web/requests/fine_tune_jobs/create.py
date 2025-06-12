from pydantic import BaseModel


class FineTuneJobCreateRequest(BaseModel):
    provider_name: str
    model_name: str
