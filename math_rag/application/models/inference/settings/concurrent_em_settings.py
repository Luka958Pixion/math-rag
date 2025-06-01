from pydantic import BaseModel


class ConcurrentEMSettings(BaseModel):
    max_requests_per_minute: float | None = None
    max_tokens_per_minute: float | None = None
    max_num_retries: int | None = None
