from typing import TypeVar

from math_rag.application.base.assistants import BaseAssistantInput


AssistantInputType = TypeVar('AssistantInputType', bound=BaseAssistantInput)
