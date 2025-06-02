from pydantic import BaseModel


class OptunaStudySettings(BaseModel):
    storage_name: str
    study_name: str
    direction: str
    load_if_exists: bool
