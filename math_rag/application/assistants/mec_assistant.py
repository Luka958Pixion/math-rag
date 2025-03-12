from math_rag.application.base.inference import BaseUnifiedLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.models.assistants import (
    MECAssistantInput,
    MECAssistantOutput,
)
from math_rag.application.models.inference import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMResponseList,
)
from math_rag.application.services import SettingsLoaderService

from .partials import PartialBatchAssistant
from .prompts import MATH_EXPRESSION_CLASSIFICATION_PROMPT


class MathExpressionClassificationAssistant(
    PartialBatchAssistant[MECAssistantInput, MECAssistantOutput]
):
    def __init__(
        self,
        llm: BaseUnifiedLLM,
        settings_loader_service: SettingsLoaderService,
        failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        super().__init__(llm, settings_loader_service, failed_request_repository)

    def encode_to_request(
        self, input: MECAssistantInput
    ) -> LLMRequest[MECAssistantOutput]:
        prompt = MATH_EXPRESSION_CLASSIFICATION_PROMPT.format(latex=input.latex)
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[MECAssistantOutput](
                model='gpt-4o-mini',
                temperature=0.0,
                response_type=MECAssistantOutput,
                metadata={'id': input.id, 'cls': MECAssistantInput.__name__},
            ),
        )

        return request

    def decode_from_response_list(
        self, response_list: LLMResponseList[MECAssistantOutput]
    ) -> MECAssistantOutput:
        output = response_list.responses[0].content

        return output
