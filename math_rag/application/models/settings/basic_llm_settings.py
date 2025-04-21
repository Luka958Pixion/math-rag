from pydantic import BaseModel


class BasicLLMSettings(BaseModel):
    max_time: float | None = None
    max_num_retries: int | None = None
