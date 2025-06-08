from math_rag.application.base.embedants import BaseEmbedantOutput


class EmbedantOutput(BaseEmbedantOutput):
    embedding: list[float]
