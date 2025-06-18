from asyncio import gather
from logging import getLogger

from backoff import expo, full_jitter, on_exception
from httpx import AsyncClient, HTTPError, ReadTimeout, Timeout

from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.models import KatexRenderResult, KatexRenderSvgResult, KatexValidateResult


logger = getLogger(__name__)


class KatexClient(BaseKatexClient):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = Timeout(30)

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def validate(self, katex: str) -> KatexValidateResult:
        url = self.base_url + '/validate'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                content=katex.encode('utf-8'),
                headers={'Content-Type': 'text/plain'},
            )
            result = response.json() if response.status_code == 200 else None

            return KatexValidateResult(**result)

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def validate_many(self, katexes: list[str]) -> list[KatexValidateResult]:
        url = self.base_url + '/validate-many'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=katexes,  # json automatically encodes to utf-8
                headers={'Content-Type': 'application/json'},
            )

            if response.status_code == 200:
                results = response.json()

            else:
                logger.error(f'Failed with status code {response.status_code}: {response.text}')
                response.raise_for_status()

        return [KatexValidateResult(**result) for result in results]

    async def batch_validate_many(
        self, katexes: list[str], *, batch_size: int
    ) -> list[KatexValidateResult]:
        tasks = [
            self.validate_many(katexes[i : i + batch_size])
            for i in range(0, len(katexes), batch_size)
        ]
        batch_results = await gather(*tasks, return_exceptions=True)
        results: list[KatexValidateResult] = []

        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(f'Batch failed after all retries: {batch_result}', exc_info=True)
                raise batch_result

            results.extend(batch_result)

        return results

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def render(self, katex: str) -> KatexRenderResult:
        url = self.base_url + '/render'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                content=katex.encode('utf-8'),
                headers={'Content-Type': 'text/plain'},
            )
            result = response.json() if response.status_code == 200 else None

            return KatexRenderResult(**result)

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def render_many(self, katexes: list[str]) -> list[KatexRenderResult]:
        url = self.base_url + '/render-many'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=katexes,  # json automatically encodes to utf-8
                headers={'Content-Type': 'application/json'},
            )

            if response.status_code == 200:
                results = response.json()

            else:
                logger.error(f'Failed with status code {response.status_code}: {response.text}')
                response.raise_for_status()

        return [KatexRenderResult(**result) for result in results]

    async def batch_render_many(
        self, katexes: list[str], *, batch_size: int
    ) -> list[KatexRenderResult]:
        tasks = [
            self.render_many(katexes[i : i + batch_size])
            for i in range(0, len(katexes), batch_size)
        ]
        batch_results = await gather(*tasks, return_exceptions=True)
        results: list[KatexRenderResult] = []

        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(f'Batch failed after all retries: {batch_result}', exc_info=True)
                raise batch_result

            results.extend(batch_result)

        return results

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def render_svg(self, katex: str) -> KatexRenderSvgResult:
        url = self.base_url + '/render-svg'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                content=katex.encode('utf-8'),
                headers={'Content-Type': 'text/plain'},
            )
            result = response.json() if response.status_code == 200 else None

            return KatexRenderSvgResult(**result)

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def render_svg_many(self, katexes: list[str]) -> list[KatexRenderSvgResult]:
        url = self.base_url + '/render-svg-many'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=katexes,  # json automatically encodes to utf-8
                headers={'Content-Type': 'application/json'},
            )

            if response.status_code == 200:
                results = response.json()

            else:
                logger.error(f'Failed with status code {response.status_code}: {response.text}')
                response.raise_for_status()

        return [KatexRenderSvgResult(**result) for result in results]

    async def batch_render_svg_many(
        self, katexes: list[str], *, batch_size: int
    ) -> list[KatexRenderSvgResult]:
        tasks = [
            self.render_svg_many(katexes[i : i + batch_size])
            for i in range(0, len(katexes), batch_size)
        ]
        batch_results = await gather(*tasks, return_exceptions=True)
        results: list[KatexRenderSvgResult] = []

        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(f'Batch failed after all retries: {batch_result}', exc_info=True)
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
