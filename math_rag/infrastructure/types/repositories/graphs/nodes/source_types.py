from typing import TypeVar

from pydantic import BaseModel


SourceNodeType = TypeVar('SourceNodeType', bound=BaseModel)
SourceRelType = TypeVar('SourceRelType', bound=BaseModel)
