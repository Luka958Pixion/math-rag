from uuid import UUID

from pydantic import BaseModel, Field


class PBSProJobListenerEntry(BaseModel):
    job_id: UUID
    listener_classes: set[str] = Field(default_factory=set)
