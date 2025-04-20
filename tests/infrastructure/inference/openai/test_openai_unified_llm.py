import pytest

from math_rag.application.base.assistants import BaseAssistantInput, BaseAssistantOutput
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMConcurrentRequest,
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
async def test_generate(infrastructure_container: InfrastructureContainer):
    # arrange
    openai_unified_llm = infrastructure_container.openai_unified_llm()

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

    # act
    result = await openai_unified_llm.generate(
        request,
        max_time=...,
        max_num_retries=...,
    )
    response = result.response_list.responses[0]

    # assert
    assert response.content.result == 4


@pytest.mark.asyncio
async def test_concurrent_generate(infrastructure_container: InfrastructureContainer):
    # arrange
    openai_unified_llm = infrastructure_container.openai_unified_llm()

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
    concurrent_request = LLMConcurrentRequest(requests=[request])

    # act
    concurrent_result = await openai_unified_llm.concurrent_generate(
        concurrent_request,
        max_requests_per_minute=...,
        max_tokens_per_minute=...,
        max_num_retries=...,
    )
    response = concurrent_result.response_lists[0].responses[0]

    # assert
    assert response.content.result == 4


@pytest.mark.asyncio
async def test_batch_generate(infrastructure_container: InfrastructureContainer):
    # arrange
    openai_unified_llm = infrastructure_container.openai_unified_llm()

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
    batch_result = await openai_unified_llm.batch_generate(
        batch_request,
        response_type=TestOutput,
        poll_interval=...,
        max_num_retries=...,
    )
    response = batch_result.response_lists[0].responses[0]

    # assert
    assert response.content.result == 4
