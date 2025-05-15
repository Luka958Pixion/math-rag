from typing import TypeVar

from pydantic import BaseModel


SourceType = TypeVar('SourceType', bound=BaseModel)
