from typing import TypeVar

from pydantic import BaseModel


InternalType = TypeVar('InternalType', bound=BaseModel)
