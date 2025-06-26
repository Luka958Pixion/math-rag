from httpx import AsyncClient, Timeout


class PushgatewayClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.timeout = Timeout(10.0)

    async def create_job(self, job: str, data: str):
        url = f'{self.base_url}/metrics/job/{job}'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url, content=data.encode('utf-8'), headers={'Content-Type': 'text/plain'}
            )
            response.raise_for_status()

    async def delete_job(self, job: str):
        url = f'{self.base_url}/metrics/job/{job}'

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(url)
            response.raise_for_status()
