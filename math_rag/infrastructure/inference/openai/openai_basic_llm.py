from backoff import expo, on_exception
from openai import AsyncOpenAI

from math_rag.application.base.inference import BaseBasicLLM
from math_rag.application.enums.inference import LLMErrorRetryPolicy
from math_rag.application.models.inference import (
    LLMError,
    LLMFailedRequest,
    LLMRequest,
    LLMResponseList,
    LLMResult,
    LLMTextResponse,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.constants.inference.openai import (
    OPENAI_API_ERRORS_TO_NOT_RETRY,
    OPENAI_API_ERRORS_TO_RAISE,
    OPENAI_API_ERRORS_TO_RETRY,
    OPENAI_ERRORS_TO_NOT_RETRY,
)
from math_rag.infrastructure.mappings.inference.openai import (
    LLMRequestMapping,
    LLMResponseListMapping,
)
from math_rag.infrastructure.validators.inference.openai import OpenAIModelNameValidator


class OpenAIBasicLLM(BaseBasicLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def generate(
        self,
        request: LLMRequest[LLMResponseType],
        *,
        max_time: float,
        max_num_retries: int,
    ) -> LLMResult[LLMResponseType]:
        OpenAIModelNameValidator.validate(request.params.model)

        @on_exception(
            wait_gen=expo,
            exception=OPENAI_API_ERRORS_TO_RETRY,
            max_time=max_time,
            max_tries=max_num_retries,
        )
        async def _generate(
            request: LLMRequest[LLMResponseType],
        ) -> LLMResponseList[LLMResponseType]:
            request_dict = LLMRequestMapping[LLMResponseType].to_target(request)
            chat_completion_callback = (
                self.client.chat.completions.create
                if request.params.response_type is LLMTextResponse
                else self.client.beta.chat.completions.parse
            )
            chat_completion = await chat_completion_callback(**request_dict)
            response_list = LLMResponseListMapping[LLMResponseType].to_source(
                chat_completion,
                request_id=request.id,
                response_type=request.params.response_type,
            )

            return response_list

        try:
            response_list = await _generate(request)
            failed_request = None

        except OPENAI_API_ERRORS_TO_RETRY as e:
            response_list = LLMResponseList[LLMResponseType](responses=[])
            error = LLMError(
                message=e.message,
                code=e.code,
                body=e.body,
                retry_policy=LLMErrorRetryPolicy.RETRY,
            )
            failed_request = LLMFailedRequest(request=request, errors=[error])
            pass

        except OPENAI_API_ERRORS_TO_NOT_RETRY as e:
            response_list = LLMResponseList[LLMResponseType](responses=[])
            error = LLMError(
                message=e.message,
                code=e.code,
                body=e.body,
                retry_policy=LLMErrorRetryPolicy.NO_RETRY,
            )
            failed_request = LLMFailedRequest(request=request, errors=[error])
            pass

        except OPENAI_ERRORS_TO_NOT_RETRY as e:
            response_list = LLMResponseList[LLMResponseType](responses=[])
            error = LLMError(
                message=str(e),
                code=None,
                body=None,
                retry_policy=LLMErrorRetryPolicy.NO_RETRY,
            )
            failed_request = LLMFailedRequest(request=request, errors=[error])
            pass

        except OPENAI_API_ERRORS_TO_RAISE:
            raise

        result = LLMResult(
            request_id=request.id,
            response_list=response_list,
            failed_request=failed_request,
        )

        return result
