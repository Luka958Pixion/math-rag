from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class PBSProVariableList(BaseModel):
    """
    PBS Pro 2024.1.0 Environment Variables

    Reference:
        https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf#page=245
    """

    home: Path | None = Field(default=None, alias='PBS_O_HOME')
    paths: list[Path] | None = Field(default=None, alias='PBS_O_PATH')
    mail: str | None = Field(default=None, alias='PBS_O_MAIL')
    shell: str | None = Field(default=None, alias='PBS_O_SHELL')
    workdir: Path | None = Field(default=None, alias='PBS_O_WORKDIR')
    host: str | None = Field(default=None, alias='PBS_O_HOST')
    lang: str | None = Field(default=None, alias='PBS_O_LANG')
    logname: str | None = Field(default=None, alias='PBS_O_LOGNAME')
    system: str | None = Field(default=None, alias='PBS_O_SYSTEM')
    queue: str | None = Field(default=None, alias='PBS_O_QUEUE')
    tz: str | None = Field(default=None, alias='PBS_O_TZ')

    environment: str | None = Field(default=None, alias='PBS_ENVIRONMENT')
    jobdir: Path | None = Field(default=None, alias='PBS_JOBDIR')
    jobid: str | None = Field(default=None, alias='PBS_JOBID')
    jobname: str | None = Field(default=None, alias='PBS_JOBNAME')
    nodefile: Path | None = Field(default=None, alias='PBS_NODEFILE')
    execution_queue: str | None = Field(default=None, alias='PBS_QUEUE')
    tmpdir: Path | None = Field(default=None, alias='PBS_TMPDIR')

    @field_validator('paths', mode='before')
    @classmethod
    def split_path(cls, value: str | None) -> list[Path] | None:
        if not value:
            return None

        return [Path(path) for path in value.split(':') if path]
