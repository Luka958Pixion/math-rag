from json import dump, load
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


class JSONReaderUtil:
    @staticmethod
    def read(path: Path, *, model: type[T]) -> T:
        with open(path, 'r') as file:
            data = load(file)

            return model(**data)


class JSONWriterUtil:
    @staticmethod
    def write(path: Path, *, model: BaseModel):
        with open(path, 'w') as file:
            dump(model.model_dump(), file, indent=4)
