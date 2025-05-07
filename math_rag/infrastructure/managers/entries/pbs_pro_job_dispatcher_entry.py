from uuid import UUID

from pydantic import BaseModel, Field


class PBSProJobDispatcherEntry(BaseModel):
    job_id: UUID
    listener_classes: set[str] = Field(default_factory=set)
