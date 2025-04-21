from pydantic import BaseModel


class BatchLLMSettings(BaseModel):
    poll_interval: float | None
    max_num_retries: int | None
