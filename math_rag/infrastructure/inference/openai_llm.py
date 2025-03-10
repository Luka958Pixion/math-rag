from backoff import expo, on_exception
from openai import AsyncOpenAI

from math_rag.application.base.inference import BaseLLM
from math_rag.application.models.inference import (
    LLMRequest,
    LLMResponseList,
    LLMTextResponse,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.inference.constants import (
    OPENAI_ERRORS_TO_RAISE,
    OPENAI_ERRORS_TO_RETRY,
)
from math_rag.infrastructure.mappings.inference import LLMResponseListMapping


retry = on_exception(
    wait_gen=expo, exception=OPENAI_ERRORS_TO_RETRY, max_time=60, max_tries=6
)


class OpenAILLM(BaseLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def _generate_text(
        self,
        request: LLMRequest[LLMResponseType],
    ) -> LLMResponseList[LLMResponseType]:
        completion = await self.client.chat.completions.create(
            model=request.params.model,
            messages=[
                {'role': message.role, 'content': message.content}
                for message in request.conversation.messages
            ],
            response_format={'type': 'text'},
            temperature=request.params.temperature,
            logprobs=request.params.top_logprobs is not None,
            top_logprobs=request.params.top_logprobs,
            reasoning_effort=request.params.reasoning_effort,
            max_completion_tokens=request.params.max_completion_tokens,
        )
        response_list = LLMResponseListMapping[LLMResponseType].to_source(completion)

        return response_list

    async def _generate_json(
        self,
        request: LLMRequest[LLMResponseType],
    ) -> LLMResponseList[LLMResponseType]:
        parsed_completion = await self.client.beta.chat.completions.parse(
            model=request.params.model,
            messages=[
                {'role': message.role, 'content': message.content}
                for message in request.conversation.messages
            ],
            response_format=request.params.response_type,
            temperature=request.params.temperature,
            logprobs=request.params.top_logprobs is not None,
            top_logprobs=request.params.top_logprobs,
            reasoning_effort=request.params.reasoning_effort,
            max_completion_tokens=request.params.max_completion_tokens,
        )
        response_list = LLMResponseListMapping[LLMResponseType].to_source(
            parsed_completion
        )

        return response_list

    @retry
    async def _generate(
        self,
        request: LLMRequest[LLMResponseType],
    ) -> LLMResponseList[LLMResponseType]:
        try:
            response_list = (
                await self._generate_text(request)
                if request.params.response_type is LLMTextResponse
                else await self._generate_json(request)
            )

        except OPENAI_ERRORS_TO_RAISE:
            raise

        return response_list

    async def generate(
        self,
        request: LLMRequest[LLMResponseType],
    ) -> LLMResponseList[LLMResponseType] | None:
        response_list = None

        try:
            response_list = (
                await self._generate_text(request)
                if request.params.response_type is LLMTextResponse
                else await self._generate_json(request)
            )

        except OPENAI_ERRORS_TO_RETRY as e:
            # TODO save errors
            pass

        return response_list
