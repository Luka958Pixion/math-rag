from math_rag.application.base.inference import BaseUnifiedLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.base.services import BaseSettingsLoaderService
from math_rag.application.models.assistants import (
    KCAssistantInput,
    KCAssistantOutput,
)
from math_rag.application.models.inference import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMResponseList,
)

from .partials import PartialUnifiedAssistant
from .prompts import KATEX_CORRECTION_PROMPT


class KCAssistant(PartialUnifiedAssistant[KCAssistantInput, KCAssistantOutput]):
    def __init__(
        self,
        llm: BaseUnifiedLLM,
        settings_loader_service: BaseSettingsLoaderService,
        failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        super().__init__(llm, settings_loader_service, failed_request_repository)

    def encode_to_request(
        self, input: KCAssistantInput
    ) -> LLMRequest[KCAssistantOutput]:
        prompt = KATEX_CORRECTION_PROMPT.format(katex=input.katex, error=input.error)
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[KCAssistantOutput](
                model='gpt-4o-mini',
                temperature=0.0,
                response_type=KCAssistantOutput.bind(input.id),
                metadata={'input_id': str(input.id)},
                store=True,
            ),
        )

        return request

    def decode_from_response_list(
        self, response_list: LLMResponseList[KCAssistantOutput]
    ) -> KCAssistantOutput:
        content = response_list.responses[0].content
        content_dict = content.model_dump(exclude_unset=True)
        output = KCAssistantOutput(**content_dict)

        return output
