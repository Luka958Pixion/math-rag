from math_rag.application.models.inference import LLMPrompt, LLMPromptCollection


_SYSTEM_PROMPT_TEMPLATE = """
You are an expert LaTeX expression classification assistant.
Given a LaTeX expression, classify it into one of five classes:
1. equality - any expression containing an equality symbol
2. inequality - any expression containing an inequality symbol
3. constant - any expression consisting exclusively of numeric constants, treat anything non-numeric such as \pi, \e or \infty as a variable
4. variable - a single variable
5. other

Return the class only (no symbols or extra text)!
"""

_USER_PROMPT_TEMPLATE = """
### LaTeX:
{latex}

### Class:
"""

_SYSTEM_PROMPT = LLMPrompt(
    template=_SYSTEM_PROMPT_TEMPLATE.strip(),
    input_keys=[],
)

_USER_PROMPT = LLMPrompt(
    template=_USER_PROMPT_TEMPLATE.strip(),
    input_keys=['latex'],
)

MATH_EXPRESSION_LABELER_PROMPTS = LLMPromptCollection(system=_SYSTEM_PROMPT, user=_USER_PROMPT)
