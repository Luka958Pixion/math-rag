from math_rag.application.models.embedders.base import BaseEmbedderOutput


class EmbedderOutput(BaseEmbedderOutput):
    embedding: list[float]
