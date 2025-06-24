from math_rag.application.models.inference import LLMPrompt, LLMPromptCollection


_SYSTEM_PROMPT_TEMPLATE = """
You are an expert at optimizing text descriptions for vector-search embedding.

Your task is to refine a provided description by removing all non-essential phrasing and meta commentary, while preserving every factual detail exactly as given.

### Instructions:
- Eliminate filler language and introductory or self-referential statements (e.g., "This description...").
- Retain all information and nuance present in the input.
- Produce a concise, information-dense output optimized for embedding and retrieval.
"""

_USER_PROMPT_TEMPLATE = """
### Original description:
{description}

### Optimized description:
"""

_SYSTEM_PROMPT = LLMPrompt(
    template=_SYSTEM_PROMPT_TEMPLATE.strip(),
    input_keys=[],
)

_USER_PROMPT = LLMPrompt(
    template=_USER_PROMPT_TEMPLATE.strip(),
    input_keys=['description'],
)

MATH_EXPRESSION_DESCRIPTION_OPTIMIZER_PROMPTS = LLMPromptCollection(
    system=_SYSTEM_PROMPT,
    user=_USER_PROMPT,
)
