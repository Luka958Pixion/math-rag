from typing import TypeVar

from pydantic import BaseModel


AssistantInputType = TypeVar('AssistantInputType', bound=BaseModel)
