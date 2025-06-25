from json import load
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


class JSONReaderUtil:
    @staticmethod
    def read(path: Path, model: type[T]) -> T:
        with open(path, 'r') as file:
            data = load(file)

            return model(**data)
