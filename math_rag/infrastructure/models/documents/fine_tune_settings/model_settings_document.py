from math_rag.infrastructure.base import BaseDocument


class ModelSettingsDocument(BaseDocument):
    model_name: str
    target_modules: list[str]
    max_tokens: int
