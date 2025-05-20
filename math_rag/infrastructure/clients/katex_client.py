from asyncio import gather
from logging import getLogger

from backoff import expo, full_jitter, on_exception
from httpx import AsyncClient, HTTPError, ReadTimeout, Timeout

from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.models import KatexValidationResult


logger = getLogger(__name__)


class KatexClient(BaseKatexClient):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = Timeout(30)

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def validate(self, katex: str) -> KatexValidationResult:
        url = self.base_url + '/validate'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                content=katex.encode('utf-8'),
                headers={'Content-Type': 'text/plain'},
            )
            result = response.json()

            return KatexValidationResult(**result)

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def validate_many(self, katexes: list[str]) -> list[KatexValidationResult]:
        url = self.base_url + '/validate-many'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=katexes,  # json automatically encodes to utf-8
                headers={'Content-Type': 'application/json'},
            )
            results = response.json()

        return [KatexValidationResult(**result) for result in results]

    async def batch_validate_many(
        self, katexes: list[str], *, batch_size: int
    ) -> list[KatexValidationResult]:
        tasks = [
            self.validate_many(katexes[i : i + batch_size])
            for i in range(0, len(katexes), batch_size)
        ]
        batch_results = await gather(*tasks, return_exceptions=True)
        results: list[KatexValidationResult] = []

        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(
                    f'Batch failed after all retries: {batch_result}', exc_info=True
                )
                raise batch_result

            results.extend(batch_result)

        return results

    async def health(self) -> bool:
        url = self.base_url + '/health'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()

            return result['status'] == 'ok'
