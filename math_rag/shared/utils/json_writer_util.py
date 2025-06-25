from json import dump
from pathlib import Path

from pydantic import BaseModel


class JSONWriterUtil:
    @staticmethod
    def write(path: Path, *, model: BaseModel):
        with open(path, 'w') as file:
            dump(model.model_dump(), file, indent=4)
