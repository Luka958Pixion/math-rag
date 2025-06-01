from pydantic import BaseModel


class BatchLLMSettings(BaseModel):
    poll_interval: float | None = None
    max_tokens_per_day: float | None = None
    max_input_file_size: int | None = None
    max_num_retries: int | None = None
