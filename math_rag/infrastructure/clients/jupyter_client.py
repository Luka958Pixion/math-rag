from asyncio import gather
from logging import getLogger

from backoff import expo, full_jitter, on_exception
from httpx import AsyncClient, HTTPError, ReadTimeout, Timeout

from math_rag.application.base.clients import BaseJupyterClient
from math_rag.application.models.clients import (
    KatexRenderResult,
    KatexRenderSvgResult,
    KatexValidateResult,
)


logger = getLogger(__name__)


class JupyterClient(BaseJupyterClient):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = Timeout(30)

    # TODO WIP
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

    async def health(self) -> bool:
        url = self.base_url + '/health'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()

            return result['status'] == 'ok'
