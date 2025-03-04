from httpx import AsyncClient, RequestError

from math_rag.application.base.services import BaseKatexValidatorService
from math_rag.application.models import KatexValidationResult


class KatexValidatorService(BaseKatexValidatorService):
    async def validate(self, katex: str) -> KatexValidationResult:
        url = 'http://localhost:3000/validate'

        try:
            async with AsyncClient() as client:
                response = await client.post(
                    url,
                    content=katex.encode('utf-8'),
                    headers={'Content-Type': 'text/plain'},
                )
                result = response.json()

                return KatexValidationResult(**result)

        except RequestError:
            raise

    async def validate_many(self, katexes: list[str]) -> list[KatexValidationResult]:
        url = 'http://localhost:3000/validate-many'

        try:
            async with AsyncClient() as client:
                response = await client.post(
                    url,
                    json=katexes,  # json automatically encodes to utf-8
                    headers={'Content-Type': 'application/json'},
                )
                results = response.json()

            return [KatexValidationResult(**result) for result in results]

        except RequestError:
            raise
