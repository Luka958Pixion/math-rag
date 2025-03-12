from pydantic import BaseModel


class ConcurrentLLMSettings(BaseModel):
    max_requests_per_minute: float
    max_tokens_per_minute: float
    max_num_retries: int
