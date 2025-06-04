from abc import ABC

from qdrant_client.http.models import PointStruct


class BaseEmbedding(ABC, PointStruct):
    pass
