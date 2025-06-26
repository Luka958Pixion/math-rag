from httpx import AsyncClient, Timeout


class PrometheusAdminClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.timeout = Timeout(10.0)

    async def delete_series(self, matchers: list[str]):
        url = f'{self.base_url}/api/v1/admin/tsdb/delete_series'
        params = [('match[]', matcher) for matcher in matchers]

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, params=params)
            response.raise_for_status()

    async def clean_tombstones(self):
        url = f'{self.base_url}/api/v1/admin/tsdb/clean_tombstones'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url)
            response.raise_for_status()
