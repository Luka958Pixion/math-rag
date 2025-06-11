from pydantic import BaseModel


class OptunaStudySettings(BaseModel):
    storage: str
    study_name: str
    direction: str
    load_if_exists: bool
