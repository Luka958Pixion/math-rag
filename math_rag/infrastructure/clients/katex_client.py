from asyncio import gather

from httpx import AsyncClient

from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.models import KatexValidationResult


class KatexClient(BaseKatexClient):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def validate(self, katex: str) -> KatexValidationResult:
        url = self.base_url + '/validate'

        async with AsyncClient() as client:
            response = await client.post(
                url,
                content=katex.encode('utf-8'),
                headers={'Content-Type': 'text/plain'},
            )
            result = response.json()

            return KatexValidationResult(**result)

    async def validate_many(self, katexes: list[str]) -> list[KatexValidationResult]:
        url = self.base_url + '/validate-many'

        async with AsyncClient() as client:
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
        batch_results = await gather(*tasks)
        results = [result for batch in batch_results for result in batch]

        return results

    async def health(self) -> bool:
        url = self.base_url + '/health'

        async with AsyncClient() as client:
            response = await client.get(url)
            result = response.json()

            return result['status'] == 'ok'
