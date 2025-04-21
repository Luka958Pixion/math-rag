from pydantic import BaseModel


class BasicEMSettings(BaseModel):
    max_time: float | None
    max_num_retries: int | None
