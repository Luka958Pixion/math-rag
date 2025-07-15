from pydantic import BaseModel


class JupyterEndSessionResult(BaseModel):
    message: str
