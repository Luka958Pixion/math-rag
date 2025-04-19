import pytest

from math_rag.application.models.inference import EMParams, EMRequest
from math_rag.infrastructure.containers import InfrastructureContainer


@pytest.mark.asyncio
async def test_embed():
    # arrange
    container = InfrastructureContainer()
    container.init_resources()
    openai_unified_em = container.openai_unified_em()

    request = EMRequest(text='test', params=EMParams(model='text-embedding-3-large'))

    # act
    result = await openai_unified_em.embed(
        request,
        max_time=2 * 60,
        max_num_retries=0,
    )
    response = result.response_list.responses[0]

    # assert
    assert len(response.embedding) == 3072
