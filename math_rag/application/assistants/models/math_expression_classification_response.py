from pydantic import BaseModel, Field


class MathExpressionClassificationResponse(BaseModel):
    label: str = Field(alias='class')
