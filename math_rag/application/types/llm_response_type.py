from typing import TypeVar

from pydantic import BaseModel


LLMResponseType = TypeVar('LLMResponseType', BaseModel, str)
