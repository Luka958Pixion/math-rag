from pydantic import BaseModel


class DatasetSettings(BaseModel):
    dataset_name: str
    config_name: str
