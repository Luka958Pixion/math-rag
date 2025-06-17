from pydantic import BaseModel


class ChoiceValue(BaseModel):
    choices: list[str]
