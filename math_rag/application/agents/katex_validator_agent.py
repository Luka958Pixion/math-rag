from agents import Agent


class KatexValidatorAgent(Agent):
    def __init__(self):
        from .tools import validate_katex_tool

        super().__init__(
            name='KatexValidatorAgent',
            model='o4-mini',
            instructions='You are an assistant for validating and fixing KaTeX in text.',
            tools=[validate_katex_tool],
        )


KATEX_VALIDATOR_INPUT_TEMPLATE = """
Validate and fix KaTeX sections in the given solution by following these steps:
1. Identify all math expressions in the given text.
2. Validate each KaTeX expression using `validate_katex_tool`.
3. Check that you have found and validated all KaTeX expressions.
4. Enclose each KaTeX expression with single `$` (for inline) or double `$$` (for multiline).
5. Do NOT add extra explanations like: "Here is the detailed solution with all KaTeX expressions properly delimited and validated."
6. Inspect the result and see if you missed some of the above requirements

Your task:
{text}
"""
