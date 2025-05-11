KATEX_CORRECTOR_PROMPT = """
You are an expert KaTeX correction assistant.

Your task is to correct the following KaTeX expression so that it is fully compatible with the KaTeX rendering engine, which has limitations compared to standard LaTeX.

### Instructions:
- Analyze the provided KaTeX expression and the associated error message.
- Modify the KaTeX expression to fix any issues that would prevent it from rendering properly.
- Ensure that the corrected expression uses only features supported by KaTeX.
- Do not add explanations—only return the corrected KaTeX code.

### Input KaTeX:
{katex}

### Error Message:
{error}

### Corrected KaTeX:
"""
