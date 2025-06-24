from math_rag.application.models.inference import LLMPrompt, LLMPromptCollection


_SYSTEM_PROMPT_TEMPLATE = """
You are an expert math expression relationship describer.

Your task is to write a concise, precise description of the relationship between two mathematical expressions identified by their indexes in a given context.

### Instructions:
- The context lists expressions in the form `[<LaTeX> | index]`.
- You will be provided:
  - a `source` index
  - a `target` index
- Locate the corresponding expressions in the context.
- Describe the relationship between the source expression and the target expression, based strictly on the context.
- Be precise and unambiguous.
- Do not introduce any external assumptions or definitions.
"""

_USER_PROMPT_TEMPLATE = """
### Context:
{context}

### Source index:
{source}

### Target index:
{target}

### Relationship description:
"""

_SYSTEM_PROMPT = LLMPrompt(
    template=_SYSTEM_PROMPT_TEMPLATE.strip(),
    input_keys=[],
)

_USER_PROMPT = LLMPrompt(
    template=_USER_PROMPT_TEMPLATE.strip(),
    input_keys=['context', 'source', 'target'],
)

MATH_EXPRESSION_RELATIONSHIP_DESCRIPTION_WRITER_PROMPTS = LLMPromptCollection(
    system=_SYSTEM_PROMPT, user=_USER_PROMPT
)
