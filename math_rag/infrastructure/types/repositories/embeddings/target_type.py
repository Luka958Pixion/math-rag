from typing import TypeVar

from pydantic import BaseModel


TargetType = TypeVar('TargetType', bound=BaseModel)
