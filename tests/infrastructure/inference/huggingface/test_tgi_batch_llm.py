import pytest

from math_rag.application.base.assistants import BaseAssistantInput, BaseAssistantOutput
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
)
from math_rag.infrastructure.containers import InfrastructureContainer


class TestInput(BaseAssistantInput):
    pass


class TestOutput(BaseAssistantOutput):
    result: int


@pytest.mark.asyncio
async def test_batch_generate(infrastructure_container: InfrastructureContainer):
    # arrange
    tgi_batch_llm = infrastructure_container.tgi_batch_llm()
    await tgi_batch_llm.initialize()

    test_input = TestInput()
    request = LLMRequest(
        conversation=LLMConversation(
            messages=[
                LLMMessage(role='system', content='You are a helpful assistant.'),
                LLMMessage(role='user', content='what is 2+2'),
            ]
        ),
        params=LLMParams(
            model='microsoft/Phi-3-mini-4k-instruct',
            temperature=0,
            response_type=TestOutput,
            max_completion_tokens=10,
            metadata={'input_id': str(test_input.id)},
        ),
    )
    batch_request = LLMBatchRequest(requests=[request])

    # act
    batch_result = await tgi_batch_llm.batch_generate(
        batch_request,
        response_type=TestOutput,
        poll_interval=...,
        max_num_retries=...,
    )
    response = batch_result.response_lists[0].responses[0]

    # assert
    assert response.content.result == 4
