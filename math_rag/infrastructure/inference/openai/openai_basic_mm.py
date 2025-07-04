from backoff import expo, on_exception
from openai import AsyncOpenAI

from math_rag.application.base.inference import BaseBasicMM
from math_rag.application.enums.inference import MMErrorRetryPolicy
from math_rag.application.models.inference import (
    MMError,
    MMFailedRequest,
    MMRequest,
    MMResponseList,
    MMResult,
)
from math_rag.infrastructure.constants.inference.openai import (
    OPENAI_API_ERRORS_TO_NOT_RETRY,
    OPENAI_API_ERRORS_TO_RAISE,
    OPENAI_API_ERRORS_TO_RETRY,
)
from math_rag.infrastructure.mappings.inference.openai import (
    MMRequestMapping,
    MMResponseListMapping,
)
from math_rag.infrastructure.validators.inference.openai import OpenAIModelNameValidator


class OpenAIBasicMM(BaseBasicMM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def moderate(
        self,
        request: MMRequest,
        *,
        max_time: float,
        max_num_retries: int,
    ) -> MMResult:
        OpenAIModelNameValidator.validate(request.params.model)

        @on_exception(
            wait_gen=expo,
            exception=OPENAI_API_ERRORS_TO_RETRY,
            max_time=max_time,
            max_tries=max_num_retries,
        )
        async def _moderate(
            request: MMRequest,
        ) -> MMResponseList:
            request_dict = MMRequestMapping.to_target(request)
            create_moderation_response = await self.client.moderations.create(**request_dict)
            response_list = MMResponseListMapping.to_source(
                create_moderation_response,
                request_id=request.id,
            )

            return response_list

        try:
            response_list = await _moderate(request)
            failed_request = None

        except OPENAI_API_ERRORS_TO_RETRY as e:
            response_list = MMResponseList(responses=[])
            error = MMError(
                message=e.message,
                code=e.code,
                body=e.body,
                retry_policy=MMErrorRetryPolicy.RETRY,
            )
            failed_request = MMFailedRequest(request=request, errors=[error])
            pass

        except OPENAI_API_ERRORS_TO_NOT_RETRY as e:
            response_list = MMResponseList(responses=[])
            error = MMError(
                message=e.message,
                code=e.code,
                body=e.body,
                retry_policy=MMErrorRetryPolicy.NO_RETRY,
            )
            failed_request = MMFailedRequest(request=request, errors=[error])
            pass

        except OPENAI_API_ERRORS_TO_RAISE:
            raise

        return MMResult(
            request_id=request.id,
            response_list=response_list,
            failed_request=failed_request,
        )
