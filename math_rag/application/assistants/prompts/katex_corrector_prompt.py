from math_rag.application.models.inference import LLMPrompt, LLMPromptCollection


_SYSTEM_PROMPT_TEMPLATE = """
You are an expert KaTeX correction assistant.

Your task is to correct the following KaTeX expression so that it is fully compatible with the KaTeX rendering engine, which has limitations compared to standard LaTeX.

### Instructions:
- Analyze the provided KaTeX expression and the associated error message.
- Modify the KaTeX expression to fix any issues that would prevent it from rendering properly.
- Ensure that the corrected expression uses only features supported by KaTeX.
- Do not add explanations—only return the corrected KaTeX code.
"""

_USER_PROMPT_TEMPLATE = """
### Input KaTeX:
{katex}

### Error Message:
{error}

### Corrected KaTeX:
"""

_SYSTEM_PROMPT = LLMPrompt(
    template=_SYSTEM_PROMPT_TEMPLATE.strip(),
    input_keys=[],
)

_USER_PROMPT = LLMPrompt(template=_USER_PROMPT_TEMPLATE.strip(), input_keys=['katex', 'error'])

KATEX_CORRECTOR_PROMPTS = LLMPromptCollection(system=_SYSTEM_PROMPT, user=_USER_PROMPT)
