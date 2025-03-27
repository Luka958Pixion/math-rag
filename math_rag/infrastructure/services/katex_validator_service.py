from asyncio import gather

from httpx import AsyncClient

from math_rag.application.base.services import BaseKatexValidatorService
from math_rag.application.models import KatexValidationResult


class KatexValidatorService(BaseKatexValidatorService):
    async def validate(self, katex: str) -> KatexValidationResult:
        url = 'http://localhost:7025/validate'

        async with AsyncClient() as client:
            response = await client.post(
                url,
                content=katex.encode('utf-8'),
                headers={'Content-Type': 'text/plain'},
            )
            result = response.json()

            return KatexValidationResult(**result)

    async def validate_many(self, katexes: list[str]) -> list[KatexValidationResult]:
        url = 'http://localhost:7025/validate-many'

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
