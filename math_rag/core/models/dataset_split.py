from pydantic import BaseModel, model_validator


class DatasetSplit(BaseModel):
    name: str
    ratio: float

    @model_validator(mode='after')
    def check_ratio(self) -> 'DatasetSplit':
        if not 0.0 < self.ratio < 1.0:
            raise ValueError(f'Ratio {self.ratio} is not in interval <0, 1>')

        return self
