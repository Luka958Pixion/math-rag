from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .settings.fine_tune_settings import FineTuneSettings


class FineTuneJob(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    settings: FineTuneSettings
