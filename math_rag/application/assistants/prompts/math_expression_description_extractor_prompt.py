from math_rag.application.models.inference import LLMPrompt


_SYSTEM_PROMPT_TEMPLATE = """
You are an expert KaTeX correction assistant.

Your task is to correct the following KaTeX expression so that it is fully compatible with the KaTeX rendering engine, which has limitations compared to standard LaTeX.

### Instructions:
- Analyze the provided KaTeX expression and the associated error message.
- Modify the KaTeX expression to fix any issues that would prevent it from rendering properly.
- Ensure that the corrected expression uses only features supported by KaTeX.
- Do not add explanations—only return the corrected KaTeX code.
"""

M_USER_PROMPT_TEMPLATE = """
### Input KaTeX:
{katex}

### Error Message:
{error}

### Corrected KaTeX:
"""

MATH_EXPRESSION_DESCRIPTION_EXTRACTOR_SYSTEM_PROMPT = LLMPrompt(
    template=_SYSTEM_PROMPT_TEMPLATE.strip(), input_keys=[]
)

MATH_EXPRESSION_DESCRIPTION_EXTRACTOR_USER_PROMPT = LLMPrompt(
    template=M_USER_PROMPT_TEMPLATE.strip(), input_keys=['katex', 'error']
)
