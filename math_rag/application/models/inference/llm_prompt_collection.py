from pydantic import BaseModel

from .llm_prompt import LLMPrompt


class LLMPromptCollection(BaseModel):
    system: LLMPrompt
    user: LLMPrompt
