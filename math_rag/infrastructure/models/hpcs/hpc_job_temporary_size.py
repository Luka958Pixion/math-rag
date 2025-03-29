from pathlib import Path

from pydantic import BaseModel


class HPCJobTemporarySize(BaseModel):
    job_id: int
    mem: int
    path: Path
