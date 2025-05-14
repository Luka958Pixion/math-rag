from math_rag.application.models.inference import LLMPrompt


MATH_EXPRESSION_LABELER_PROMPT_TEMPLATE = """
You are an expert LaTeX expression classification assistant.
Given a LaTeX expression, classify it into one of five classes:
{class_names}

Return the class number only (no symbols or extra text)!

### LaTeX:
{latex}

### Class:
"""

MATH_EXPRESSION_LABELER_PROMPT = LLMPrompt(
    template=MATH_EXPRESSION_LABELER_PROMPT_TEMPLATE,
    input_keys=['class_names', 'latex'],
)
