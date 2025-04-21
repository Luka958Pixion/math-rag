from pydantic import BaseModel


class BatchEMSettings(BaseModel):
    poll_interval: float | None
    max_num_retries: int | None
