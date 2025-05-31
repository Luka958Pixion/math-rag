from abc import ABC
from io import BytesIO
from typing import Any

from minio.commonconfig import Tags
from minio.helpers import DictType, ProgressType
from minio.retention import Retention
from minio.sse import Sse
from pydantic import BaseModel


class BaseObject(ABC, BaseModel):
    object_name: str
    data: BytesIO
    length: int
    content_type: str = 'application/octet-stream'
    metadata: DictType | None = None
    sse: Sse | None = None
    progress: Any | None = None  # ProgressType doesn't work with Pydantic
    part_size: int = 0
    num_parallel_uploads: int = 3
    tags: Tags | None = None
    retention: Retention | None = None
    legal_hold: bool = False

    class Config:
        arbitrary_types_allowed = True  # needed for BinaryIO
