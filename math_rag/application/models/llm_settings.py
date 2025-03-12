from pydantic import BaseModel


class LLMSettings(BaseModel):
    max_time: float
    max_num_retries: int
