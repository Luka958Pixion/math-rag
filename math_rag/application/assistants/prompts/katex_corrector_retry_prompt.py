from math_rag.application.models.inference import LLMPrompt


_USER_PROMPT_TEMPLATE = """
Your KaTeX is still not rendering properly, fix it.

### Error Message:
{error}

### Corrected KaTeX:
"""


KATEX_CORRECTOR_RETRY_USER_PROMPT = LLMPrompt(
    template=_USER_PROMPT_TEMPLATE.strip(),
    input_keys=['error'],
)
