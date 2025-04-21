from pydantic import BaseModel


class BatchEMSettings(BaseModel):
    poll_interval: float
    max_num_retries: int
