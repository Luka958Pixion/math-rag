from pathlib import Path

from pydantic import BaseModel


class MathExpressionIndexBuildDetails(BaseModel):
    file_path: Path
