from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel
from yaml import safe_load


T = TypeVar('T', bound=BaseModel)


class YAMLReaderUtil:
    @staticmethod
    def read(path: Path, *, model: type[T]) -> T:
        with open(path, 'r') as file:
            yaml_dict = safe_load(file)

        return model(**yaml_dict)
