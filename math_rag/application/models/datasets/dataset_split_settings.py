from pydantic import BaseModel


class DatasetSplitSettings(BaseModel):
    train_ratio: float
    validate_ratio: float
    test_ratio: float
    seed: int
