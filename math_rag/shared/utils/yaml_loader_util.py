from pathlib import Path
from typing import Type, TypeVar

from pydantic import BaseModel
from yaml import safe_load


T = TypeVar('T', bound=BaseModel)


class YamlLoaderUtil:
    @staticmethod
    def load(path: Path, *, model: Type[T]) -> T:
        with open(path) as file:
            yaml_dict = safe_load(file)

        return model(**yaml_dict)
