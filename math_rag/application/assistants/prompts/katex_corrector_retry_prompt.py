from math_rag.application.models.inference import LLMPrompt


KATEX_CORRECTOR_RETRY_PROMPT_TEMPLATE = """
Your KaTeX is still not rendering properly, fix it.

### Error Message:
{error}

### Corrected KaTeX:
"""

KATEX_CORRECTOR_RETRY_PROMPT = LLMPrompt(
    template=KATEX_CORRECTOR_RETRY_PROMPT_TEMPLATE, input_keys=['error']
)
