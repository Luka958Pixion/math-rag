from pydantic import BaseModel


class Settings(BaseModel):
    max_requests_per_minute = (...,)
    max_tokens_per_minute = (...,)
    max_num_retries = (...,)

    poll_interval = (...,)
    max_num_retries = (...,)

    max_time = ...  # 60, 6
    max_num_retries = ...
