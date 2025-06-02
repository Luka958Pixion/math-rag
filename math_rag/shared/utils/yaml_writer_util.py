from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel
from yaml import safe_dump


T = TypeVar('T', bound=BaseModel)


class YamlWriterUtil:
    @staticmethod
    def write(path: Path, *, model: T):
        with open(path, 'w') as file:
            safe_dump(model.model_dump(), file)
