from backoff import expo, on_exception
from openai import AsyncOpenAI

from math_rag.application.base.inference import BaseLLM
from math_rag.application.models.inference import (
    LLMError,
    LLMFailedRequest,
    LLMRequest,
    LLMResponseList,
    LLMResult,
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


class OpenAILLM(BaseLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def generate(
        self,
        request: LLMRequest[LLMResponseType],
        *,
        max_time: float,
        max_num_retries: int,
    ) -> LLMResult[LLMResponseType]:
        response_list = []
        failed_request = None

        @on_exception(
            wait_gen=expo,
            exception=OPENAI_ERRORS_TO_RETRY,
            max_time=max_time,
            max_tries=max_num_retries,
        )
        async def _generate(
            request: LLMRequest[LLMResponseType],
        ) -> LLMResponseList[LLMResponseType]:
            request_dict = LLMRequestMapping[LLMResponseType].to_target(request)
            completion_callback = (
                self.client.chat.completions.create
                if request.params.response_type is LLMTextResponse
                else self.client.beta.chat.completions.parse
            )
            completion = await completion_callback(**request_dict)
            response_list = LLMResponseListMapping[LLMResponseType].to_source(
                completion,
                request_id=request.id,
                response_type=request.params.response_type,
            )

            return response_list

        try:
            response_list = await _generate(request)

        except OPENAI_ERRORS_TO_RETRY as e:
            response_list = LLMResponseList[LLMResponseType](responses=[])
            error = LLMError(message=e.message, body=e.body)
            failed_request = LLMFailedRequest(request=request, errors=[error])
            pass

        except OPENAI_ERRORS_TO_RAISE:
            raise

        result = LLMResult(response_list=response_list, failed_request=failed_request)

        return result
