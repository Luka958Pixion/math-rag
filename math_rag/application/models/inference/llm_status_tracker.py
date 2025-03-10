from pydantic import BaseModel


class LLMStatusTracker(BaseModel):
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    time_of_last_rate_limit_error: int = 0
