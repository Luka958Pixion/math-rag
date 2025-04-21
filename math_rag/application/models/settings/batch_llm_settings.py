from pydantic import BaseModel


class BatchLLMSettings(BaseModel):
    poll_interval: float
    max_num_retries: int
