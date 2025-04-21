from pydantic import BaseModel

from .basic_em_settings import BasicEMSettings
from .batch_em_settings import BatchEMSettings
from .concurrent_em_settings import ConcurrentEMSettings


class EMSettings(BaseModel):
    basic: BasicEMSettings | None = None
    batch: BatchEMSettings | None = None
    concurrent: ConcurrentEMSettings | None = None
