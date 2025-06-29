from math_rag.application.models.inference import LLMPrompt, LLMPromptCollection


_SYSTEM_PROMPT_TEMPLATE = """
You are an expert math expression description writer.

Your task is to produce a precise, self-contained description of a target math expression, based strictly on the surrounding context.

### Instructions:
- The context lists expressions in the form `[<LaTeX> | index]`.
- Be concise and unambiguous.
- Only describe what can be inferred from the given context.
- Avoid introducing any external assumptions or definitions.
- Never include given math expression in description.
- Never include LaTeX in description.
"""

_USER_PROMPT_TEMPLATE = """
### Math expression of interest:
{katex}

### Math expression with surrounding context:
{context}

### Description:
"""

_SYSTEM_PROMPT = LLMPrompt(
    template=_SYSTEM_PROMPT_TEMPLATE.strip(),
    input_keys=[],
)

_USER_PROMPT = LLMPrompt(
    template=_USER_PROMPT_TEMPLATE.strip(),
    input_keys=['katex', 'context'],
)

MATH_EXPRESSION_DESCRIPTION_WRITER_PROMPTS = LLMPromptCollection(
    system=_SYSTEM_PROMPT,
    user=_USER_PROMPT,
)
