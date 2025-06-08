from math_rag.application.models.embedants.base import BaseEmbedantOutput


class EmbedantOutput(BaseEmbedantOutput):
    embedding: list[float]
