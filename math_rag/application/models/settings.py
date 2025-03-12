from pydantic import BaseModel


class Settings(BaseModel):
    max_requests_per_minute = (...,)
    max_tokens_per_minute = (...,)
    max_attempts = (...,)

    poll_interval = (...,)
    num_retries = (...,)
