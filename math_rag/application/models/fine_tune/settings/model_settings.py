from pydantic import BaseModel


class ModelSettings(BaseModel):
    model_name: str
    target_modules: list[str]
