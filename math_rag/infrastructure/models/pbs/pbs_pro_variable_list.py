from pathlib import Path

from pydantic import BaseModel, Field


class PBSProVariableList(BaseModel):
    home: Path = Field(alias='PBS_O_HOME')
    path: Path = Field(alias='PBS_O_PATH')
    mail: Path = Field(alias='PBS_O_MAIL')
    shell: Path = Field(alias='PBS_O_SHELL')
    workdir: Path = Field(alias='PBS_O_WORKDIR')
    host: str = Field(alias='PBS_O_HOST')
    lang: str = Field(alias='PBS_O_LANG')
    logname: str = Field(alias='PBS_O_LOGNAME')
    system: str = Field(alias='PBS_O_SYSTEM')
    queue: str = Field(alias='PBS_O_QUEUE')
