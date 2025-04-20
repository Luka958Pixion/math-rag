from pydantic import BaseModel


class EMSettings(BaseModel):
    max_time: float
    max_num_retries: int
