from neo4j import AsyncGraphDatabase, AsyncManagedTransaction

from math_rag.core.base import BaseGraphRepository


class GraphRepository(BaseGraphRepository):
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(uri=..., auth=...)

    async def close(self):
        await self.driver.close()

    async def _run_query(
        self, tx: AsyncManagedTransaction, query: str, parameters: dict = None
    ) -> list[dict]:
        result = await tx.run(query, parameters)

        return [record.data() async for record in result]

    async def _execute_write(self, query: str, parameters: dict = None):
        async with self.driver.session() as session:
            return await session.execute_write(self._run_query, query, parameters)

    async def _execute_read(self, query: str, parameters: dict = None):
        async with self.driver.session() as session:
            return await session.execute_read(self._run_query, query, parameters)

    async def create_node(self, name: str):
        query = """
            MERGE (p:Person {name: $name})
            RETURN p.name AS name
        """
        parameters = {'name': name}

        return await self._execute_read(query, parameters)

    async def delete_node(self, name: str):
        pass
