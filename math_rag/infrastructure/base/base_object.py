from typing import BinaryIO

from minio.commonconfig import Tags
from minio.helpers import DictType, ProgressType
from minio.retention import Retention
from minio.sse import Sse
from pydantic import BaseModel


class BaseObject(BaseModel):
    bucket_name: str
    object_name: str
    data: BinaryIO
    length: int
    content_type: str = 'application/octet-stream'
    metadata: DictType | None = None
    sse: Sse | None = None
    progress: ProgressType | None = None
    part_size: int = 0
    num_parallel_uploads: int = 3
    tags: Tags | None = None
    retention: Retention | None = None
    legal_hold: bool = False
