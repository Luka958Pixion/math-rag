from typing import TypeVar

from pydantic import BaseModel


AssistantResponseType = TypeVar('AssistantResponseType', bound=BaseModel)
