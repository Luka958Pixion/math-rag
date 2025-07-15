from pydantic import BaseModel


class JupyterExecuteCodeResult(BaseModel):
    output: str | None = None
    error: str | None = None
