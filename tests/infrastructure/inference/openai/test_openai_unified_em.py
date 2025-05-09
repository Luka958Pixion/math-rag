import pytest

from math_rag.application.models.inference import (
    EMBatchRequest,
    EMConcurrentRequest,
    EMParams,
    EMRequest,
)
from math_rag.infrastructure.containers import InfrastructureContainer


@pytest.mark.asyncio
async def test_embed(infrastructure_container: InfrastructureContainer):
    # arrange
    openai_unified_em = infrastructure_container.openai_managed_em()
    request = EMRequest(
        text='test', params=EMParams(model='text-embedding-3-large', dimensions=3072)
    )

    # act
    result = await openai_unified_em.embed(
        request,
        max_time=2 * 60,
        max_num_retries=0,
    )
    response = result.response_list.responses[0]

    # assert
    assert len(response.embedding) == 3072


@pytest.mark.asyncio
async def test_concurrent_embed(infrastructure_container: InfrastructureContainer):
    # arrange
    openai_unified_em = infrastructure_container.openai_managed_em()
    concurrent_request = EMConcurrentRequest(
        requests=[
            EMRequest(
                text='test',
                params=EMParams(model='text-embedding-3-large', dimensions=3072),
            )
        ]
    )

    # act
    concurrent_result = await openai_unified_em.concurrent_embed(
        concurrent_request,
        max_requests_per_minute=...,
        max_tokens_per_minute=...,
        max_num_retries=...,
    )
    response = concurrent_result.response_lists[0].responses[0]

    # assert
    assert len(response.embedding) == 3072


@pytest.mark.asyncio
async def test_batch_embed(infrastructure_container: InfrastructureContainer):
    # arrange
    openai_unified_em = infrastructure_container.openai_managed_em()
    batch_request = EMBatchRequest(
        requests=[
            EMRequest(
                text='test',
                params=EMParams(model='text-embedding-3-large', dimensions=3072),
            )
        ]
    )

    # act
    batch_result = await openai_unified_em.batch_embed(
        batch_request,
        poll_interval=...,
        max_num_retries=...,
    )
    response = batch_result.response_lists[0].responses[0]

    # assert
    assert len(response.embedding) == 3072
