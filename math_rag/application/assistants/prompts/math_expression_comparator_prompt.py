from math_rag.application.models.inference import LLMPrompt, LLMPromptCollection


_SYSTEM_PROMPT_TEMPLATE = """
You are an expert math-expression comparator.

Your task is to decide whether two given mathematical expressions represent exactly the same entity, based solely on their surrounding contexts.

### Instructions:
- Rely only on information inferable from the two contexts.
- Determine exact equivalence: return true if and only if they are the same entity.
- Provide a concise reason justifying your decision.
- Do not introduce external assumptions or definitions.
- Output must be valid JSON with keys "is_identical" (boolean) and "reason" (string).
"""

_USER_PROMPT_TEMPLATE = """
### First math expression:
{katex}

### Context for first expression:
{context}

### Second math expression:
{other_katex}

### Context for second expression:
{other_context}

### Decision (JSON):
{
  "is_identical": <true/false>,
  "reason": "<your explanation here>"
}
"""

_SYSTEM_PROMPT = LLMPrompt(
    template=_SYSTEM_PROMPT_TEMPLATE.strip(),
    input_keys=[],
)

_USER_PROMPT = LLMPrompt(
    template=_USER_PROMPT_TEMPLATE.strip(),
    input_keys=['katex', 'context', 'other_katex', 'other_context'],
)

MATH_EXPRESSION_COMPARATOR_PROMPTS = LLMPromptCollection(
    system=_SYSTEM_PROMPT,
    user=_USER_PROMPT,
)
