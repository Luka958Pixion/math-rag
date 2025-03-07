from typing import TypeVar

from pydantic import BaseModel


AssistantRequestType = TypeVar('AssistantRequestType', bound=BaseModel)
