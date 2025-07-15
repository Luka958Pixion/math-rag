from pydantic import BaseModel


class JupyterResetSessionResult(BaseModel):
    message: str
