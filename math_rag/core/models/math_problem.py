from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class MathProblem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_expression_index_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    file_path: Path | None
    url: str | None

    @model_validator(mode='after')
    def check_token_xor_url(cls, model: 'MathProblem') -> 'MathProblem':
        if model.file_path is not None and model.url is not None:
            raise ValueError('Either file path or url must be set')

        return model
