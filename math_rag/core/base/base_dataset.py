from abc import ABC
from uuid import UUID

from pydantic import BaseModel


class BaseDataset(BaseModel, ABC):
    build_from_id: UUID | None = None
