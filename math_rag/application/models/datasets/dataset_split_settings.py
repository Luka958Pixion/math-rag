from pydantic import BaseModel


class DatasetSplitSettings(BaseModel):
    train_ratio: float
    validation_ratio: float
    test_ratio: float
    seed: int
