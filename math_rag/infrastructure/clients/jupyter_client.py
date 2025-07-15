from logging import getLogger

from backoff import expo, full_jitter, on_exception
from httpx import AsyncClient, HTTPError, ReadTimeout, Timeout

from math_rag.application.base.clients import BaseJupyterClient
from math_rag.application.models.clients import (
    JupyterEndSessionResult,
    JupyterExecuteCodeResult,
    JupyterResetSessionResult,
    JupyterStartSessionResult,
)


logger = getLogger(__name__)


class JupyterClient(BaseJupyterClient):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = Timeout(30)

    async def _post(
        self,
        path: str,
        *,
        data: dict | None = None,
    ):
        async with AsyncClient(timeout=self.timeout) as client:
            return await client.post(f'{self.base_url}{path}', data=data)

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def start_session(self, user_id: str) -> JupyterStartSessionResult:
        response = await self._post('/start-session', data={'user_id': user_id})

        if response.status_code != 200:
            raise HTTPError(f'[{response.status_code}] {response.text}')

        return JupyterStartSessionResult(**response.json())

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def execute_code(self, user_id: str, code: str) -> JupyterExecuteCodeResult:
        response = await self._post(
            '/execute-code',
            data={'user_id': user_id, 'code': code},
        )

        if response.status_code == 200:
            return JupyterExecuteCodeResult(**response.json())

        if response.status_code in (400, 500):
            detail = None

            if response.headers.get('content-type', '').startswith('application/json'):
                body = response.json().get('detail')

                if isinstance(body, dict):
                    detail = body.get('error') or repr(body)
                else:
                    detail = body
            else:
                detail = response.text

            return JupyterExecuteCodeResult(error=str(detail))

        raise HTTPError(f'[{response.status_code}] {response.text}')

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def reset_session(self, user_id: str) -> JupyterResetSessionResult:
        response = await self._post('/reset-session', data={'user_id': user_id})

        if response.status_code != 200:
            raise HTTPError(f'[{response.status_code}] {response.text}')

        return JupyterResetSessionResult(**response.json())

    @on_exception(expo, (HTTPError, ReadTimeout), max_tries=5, jitter=full_jitter)
    async def end_session(self, user_id: str) -> JupyterEndSessionResult:
        response = await self._post('/end-session', data={'user_id': user_id})

        if response.status_code != 200:
            raise HTTPError(f'[{response.status_code}] {response.text}')

        return JupyterEndSessionResult(**response.json())

    async def health(self) -> bool:
        url = self.base_url + '/health'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()

            return result['status'] == 'ok'
