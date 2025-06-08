from typing import TypeVar

from math_rag.application.models.assistants.base import BaseAssistantInput


AssistantInputType = TypeVar('AssistantInputType', bound=BaseAssistantInput)
