from math_rag.application.models.inference import LLMPrompt


MATH_EXPRESSION_LABELER_PROMPT_TEMPLATE = """
You are an expert LaTeX expression classification assistant.
Given a LaTeX expression, classify it into one of five classes:
1. equality
2. inequality
3. constant
4. variable
5. other

Return the class number only (no symbols or extra text)!

### LaTeX:
{latex}

### Class:
"""

MATH_EXPRESSION_LABELER_PROMPT = LLMPrompt(
    template=MATH_EXPRESSION_LABELER_PROMPT_TEMPLATE.strip(),
    input_keys=['latex'],
)
