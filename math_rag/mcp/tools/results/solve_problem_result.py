from pydantic import BaseModel


class SolveProblemResult(BaseModel):
    solution: str
