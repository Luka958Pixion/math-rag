from pathlib import Path

from pydantic import BaseModel, model_validator


class MathExpressionIndexBuildDetails(BaseModel):
    file_path: Path | None
    url: str | None

    @model_validator(mode='after')
    def check_token_xor_url(
        cls, model: 'MathExpressionIndexBuildDetails'
    ) -> 'MathExpressionIndexBuildDetails':
        if model.file_path is not None and model.url is not None:
            raise ValueError('Either file path or url must be set')

        return model
