from typing import TypeVar

from pydantic import BaseModel


AssistantOutputType = TypeVar('AssistantOutputType', bound=BaseModel)
