from pathlib import Path

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
from math_rag.infrastructure.inference.huggingface import TGIBatchLLM


MODEL_HUB_ID = 'microsoft/Phi-3-mini-4k-instruct'


class SomeInput(BaseAssistantInput):
    pass


class SomeOutput(BaseAssistantOutput):
    result: int


@pytest.mark.asyncio
async def test_batch_generate_returns_response():
    # arrange
    some_input = SomeInput()
    request = LLMRequest(
        conversation=LLMConversation(
            messages=[
                LLMMessage(role='system', content='You are a helpful assistant.'),
                LLMMessage(role='user', content='what is 2+2'),
            ]
        ),
        params=LLMParams(
            model=MODEL_HUB_ID,
            temperature=0,
            response_type=SomeOutput,
            max_completion_tokens=10,
            metadata={'input_id': str(some_input.id)},
        ),
    )
    batch_request = LLMBatchRequest(requests=[request])

    container = InfrastructureContainer()
    container.init_resources()

    llm = TGIBatchLLM(
        remote=Path('tgi_default_root'),
        file_system_client=container.file_system_client(),
        pbs_pro_client=container.pbs_pro_client(),
        sftp_client=container.sftp_client(),
        apptainer_client=container.apptainer_client(),
    )

    await llm.init_resources()

    # act
    result = await llm.batch_generate(
        batch_request=batch_request,
        response_type=SomeOutput,
        poll_interval=3 * 60,
        max_num_retries=0,
    )

    # TODO assert
