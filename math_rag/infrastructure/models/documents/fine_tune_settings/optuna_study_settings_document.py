from math_rag.infrastructure.base import BaseDocument


class OptunaStudySettingsDocument(BaseDocument):
    storage: str
    study_name: str
    direction: str
    load_if_exists: bool
