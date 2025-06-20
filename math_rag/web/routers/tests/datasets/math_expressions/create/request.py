from uuid import UUID

from pydantic import BaseModel


class Request(BaseModel):
    math_expression_dataset_id: UUID
    math_expression_dataset_split_name: str
    inference_provider: str
    model_provider: str
    model: str
