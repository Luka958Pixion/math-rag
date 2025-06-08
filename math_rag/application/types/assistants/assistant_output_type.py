from typing import TypeVar

from math_rag.application.models.assistants.base import BaseAssistantOutput


AssistantOutputType = TypeVar('AssistantOutputType', bound=BaseAssistantOutput)
