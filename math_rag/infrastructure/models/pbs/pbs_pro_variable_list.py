from pathlib import Path

from pydantic import BaseModel, Field


class PBSProVariableList(BaseModel):
    """
    PBS Pro 2024.1.0 Environment Variables

    Reference:
        https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf#page=245
    """

    home: Path | None = Field(alias='PBS_O_HOME')
    path: Path | None = Field(alias='PBS_O_PATH')
    mail: Path | None = Field(alias='PBS_O_MAIL')
    shell: Path | None = Field(alias='PBS_O_SHELL')
    workdir: Path | None = Field(alias='PBS_O_WORKDIR')
    host: str | None = Field(alias='PBS_O_HOST')
    lang: str | None = Field(alias='PBS_O_LANG')
    logname: str | None = Field(alias='PBS_O_LOGNAME')
    system: str | None = Field(alias='PBS_O_SYSTEM')
    queue: str | None = Field(alias='PBS_O_QUEUE')
    tz: str | None = Field(alias='PBS_O_TZ')

    environment: str | None = Field(alias='PBS_ENVIRONMENT')
    jobdir: Path | None = Field(alias='PBS_JOBDIR')
    jobid: str | None = Field(alias='PBS_JOBID')
    jobname: str | None = Field(alias='PBS_JOBNAME')
    nodefile: Path | None = Field(alias='PBS_NODEFILE')
    execution_queue: str | None = Field(alias='PBS_QUEUE')
    tmpdir: Path | None = Field(alias='PBS_TMPDIR')
