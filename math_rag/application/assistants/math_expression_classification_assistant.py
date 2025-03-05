from math_rag.application.base.inference import BaseLLM
from math_rag.application.models import LLMParams

from .models import MathExpressionClassificationResponse
from .prompts import MATH_EXPRESSION_CLASSIFICATION_PROMPT


class MathExpressionClassificationAssistant:
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def classify(self, latex: str) -> str:
        params = LLMParams(
            model='gpt-4o-mini',
            temperature=0.0,
        )
        prompt = MATH_EXPRESSION_CLASSIFICATION_PROMPT.format(latex=latex)
        response = await self.llm.generate_json(
            prompt=prompt,
            params=params,
            response_model_type=MathExpressionClassificationResponse,
        )

        return response.label
