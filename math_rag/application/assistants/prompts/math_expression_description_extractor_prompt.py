from math_rag.application.models.inference import LLMPrompt, LLMPromptCollection


_SYSTEM_PROMPT_TEMPLATE = """
You are an expert TODO

### Instructions:
- TODO
"""

_USER_PROMPT_TEMPLATE = """
### Input:
TODO
"""

_SYSTEM_PROMPT = LLMPrompt(
    template=_SYSTEM_PROMPT_TEMPLATE.strip(),
    input_keys=[],
)

_USER_PROMPT = LLMPrompt(
    template=_USER_PROMPT_TEMPLATE.strip(),
    input_keys=[],
)

MATH_EXPRESSION_DESCRIPTION_EXTRACTOR_PROMPTS = LLMPromptCollection(
    system=_SYSTEM_PROMPT,
    user=_USER_PROMPT,
)
