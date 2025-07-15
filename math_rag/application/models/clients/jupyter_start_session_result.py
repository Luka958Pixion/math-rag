from pydantic import BaseModel


class JupyterStartSessionResult(BaseModel):
    message: str
    notebook_path: str
