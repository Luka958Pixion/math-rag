from abc import ABC
from typing import Any

from pydantic import BaseModel


class BaseEmbedding(ABC, BaseModel):
    id: str
    vector: list[float]
    payload: dict[str, Any]
