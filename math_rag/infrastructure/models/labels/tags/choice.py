from pydantic import BaseModel, Field


class Choice(BaseModel):
    """
    Label Studio <Choice> tag parameters

    Reference:
        https://labelstud.io/tags/choice
    """

    value: str
    selected: bool | None = None
    alias_: str | None = Field(None, alias='alias')
    style: str | None = None
    hotkey: str | None = None
    html: str | None = None
    hint: str | None = None
    color: str | None = None

    model_config = {'populate_by_name': True, 'populate_by_alias': True}
