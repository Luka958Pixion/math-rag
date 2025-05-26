from backoff import expo, on_exception
from openai import AsyncOpenAI

from math_rag.application.base.inference import BaseBasicEM
from math_rag.application.enums.inference import EMErrorRetryPolicy
from math_rag.application.models.inference import (
    EMError,
    EMFailedRequest,
    EMRequest,
    EMResponseList,
    EMResult,
)
from math_rag.infrastructure.constants.inference.openai import (
    OPENAI_API_ERRORS_TO_NOT_RETRY,
    OPENAI_API_ERRORS_TO_RAISE,
    OPENAI_API_ERRORS_TO_RETRY,
)
from math_rag.infrastructure.mappings.inference.openai import (
    EMRequestMapping,
    EMResponseListMapping,
)
from math_rag.infrastructure.validators.inference.openai import OpenAIModelNameValidator


class OpenAIBasicEM(BaseBasicEM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def embed(
        self,
        request: EMRequest,
        *,
        max_time: float,
        max_num_retries: int,
    ) -> EMResult:
        OpenAIModelNameValidator.validate(request.params.model)

        @on_exception(
            wait_gen=expo,
            exception=OPENAI_API_ERRORS_TO_RETRY,
            max_time=max_time,
            max_tries=max_num_retries,
        )
        async def _embed(
            request: EMRequest,
        ) -> EMResponseList:
            request_dict = EMRequestMapping.to_target(request)
            create_embedding_response = await self.client.embeddings.create(
                **request_dict
            )
            response_list = EMResponseListMapping.to_source(
                create_embedding_response,
                request_id=request.id,
            )

            return response_list

        try:
            response_list = await _embed(request)
            failed_request = None

        except OPENAI_API_ERRORS_TO_RETRY as e:
            response_list = EMResponseList(responses=[])
            error = EMError(
                message=e.message,
                code=e.code,
                body=e.body,
                retry_policy=EMErrorRetryPolicy.RETRY,
            )
            failed_request = EMFailedRequest(request=request, errors=[error])
            pass

        except OPENAI_API_ERRORS_TO_NOT_RETRY as e:
            response_list = EMResponseList(responses=[])
            error = EMError(
                message=e.message,
                code=e.code,
                body=e.body,
                retry_policy=EMErrorRetryPolicy.NO_RETRY,
            )
            failed_request = EMFailedRequest(request=request, errors=[error])
            pass

        except OPENAI_API_ERRORS_TO_RAISE:
            raise

        return EMResult(
            request_id=request.id,
            response_list=response_list,
            failed_request=failed_request,
        )
