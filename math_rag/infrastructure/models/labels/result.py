from pydantic import BaseModel

from .choice_value import ChoiceValue


class Result(BaseModel):
    id: str
    from_name: str
    to_name: str
    type: str
    value: ChoiceValue
    origin: str | None = None
