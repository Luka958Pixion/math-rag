from typing import TypeVar

from math_rag.application.base.assistants import BaseAssistantOutput


AssistantOutputType = TypeVar('AssistantOutputType', bound=BaseAssistantOutput)
