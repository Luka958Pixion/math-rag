from backoff import expo, on_exception
from openai import AsyncOpenAI

from math_rag.application.base.inference import BaseLLM
from math_rag.application.models.inference import (
    LLMError,
    LLMFailedRequest,
    LLMRequest,
    LLMResponseList,
    LLMTextResponse,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.constants.inference import (
    OPENAI_ERRORS_TO_RAISE,
    OPENAI_ERRORS_TO_RETRY,
)
from math_rag.infrastructure.mappings.inference import (
    LLMRequestMapping,
    LLMResponseListMapping,
)


retry = on_exception(
    wait_gen=expo, exception=OPENAI_ERRORS_TO_RETRY, max_time=60, max_tries=6
)


class OpenAILLM(BaseLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    @retry
    async def _generate(
        self,
        request: LLMRequest[LLMResponseType],
    ) -> LLMResponseList[LLMResponseType]:
        request_dict = LLMRequestMapping[LLMResponseType].to_target(request)
        completion_callback = (
            self.client.chat.completions.create
            if request.params.response_type is LLMTextResponse
            else self.client.beta.chat.completions.parse
        )
        completion = await completion_callback(**request_dict)
        response_list = LLMResponseListMapping[LLMResponseType].to_source(completion)

        return response_list

    async def generate(
        self,
        request: LLMRequest[LLMResponseType],
    ) -> LLMResponseList[LLMResponseType] | None:
        response_list = None

        try:
            response_list = await self._generate(request)

        except OPENAI_ERRORS_TO_RETRY as e:
            # TODO save failed_request
            error = LLMError(message=e.message, body=e.body)
            failed_request = LLMFailedRequest(request=request, errors=[error])
            pass

        except OPENAI_ERRORS_TO_RAISE:
            raise

        return response_list
