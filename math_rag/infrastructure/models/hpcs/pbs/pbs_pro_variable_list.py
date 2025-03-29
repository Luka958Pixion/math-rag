from pathlib import Path

from pydantic import BaseModel


class PBSProVariableList(BaseModel):
    """
    PBS Pro 2024.1.0 Environment Variables

    Reference:
        https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf#page=245
    """

    home: Path | None = None
    paths: list[Path] = []
    mail: Path | None = None
    shell: str | None = None
    workdir: Path | None = None
    host: str | None = None
    lang: str | None = None
    logname: str | None = None
    system: str | None = None
    queue: str | None = None
    tz: str | None = None
    environment: str | None = None
    jobdir: Path | None = None
    jobid: str | None = None
    jobname: str | None = None
    nodefile: Path | None = None
    execution_queue: str | None = None
    tmpdir: Path | None = None
