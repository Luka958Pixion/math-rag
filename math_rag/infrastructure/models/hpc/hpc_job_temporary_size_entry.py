from pathlib import Path

from pydantic import BaseModel


class HPCJobTemporarySizeEntry(BaseModel):
    job_id: int
    mem: int
    path: Path
