from typing import Generic

from neo4j import AsyncGraphDatabase
from neomodel import AsyncNodeSet, AsyncStructuredNode, db

from math_rag.application.base.repositories.graphs import BaseGraphRepository
from math_rag.infrastructure.types.repositories.graphs.nodes import (
    MappingType,
    SourceType,
    TargetType,
)


class GraphRepository(
    BaseGraphRepository[SourceType], Generic[SourceType, TargetType, MappingType]
):
    def __init__(self, uri: str, username: str, password: str):
        driver = AsyncGraphDatabase.driver(uri=uri, auth=(username, password))
        db.set_connection(driver=driver)

    async def close(self):
        await db.close_connection()

    async def insert_node(self, node: SourceType):
        # TODO map
        async with db.transaction:
            await node.save()

    async def find_nodes(
        self, model_class: type[AsyncStructuredNode], match_properties: dict
    ):  # TODO make better
        async with db.transaction:
            node_set: AsyncNodeSet = model_class.nodes

            return await node_set.filter(**match_properties).all()

    async def delete_nodes(self, model_class: type[AsyncStructuredNode], match_properties: dict):
        async with db.transaction:
            node_set: AsyncNodeSet = model_class.nodes
            nodes: list[AsyncStructuredNode] = await node_set.filter(**match_properties).all()

            for node in nodes:
                await node.delete()

    async def update_node(
        self,
        model_class: type[AsyncStructuredNode],
        match_properties: dict,
        update_properties: dict,
    ):
        async with db.transaction:
            node_set: AsyncNodeSet = model_class.nodes
            node: AsyncStructuredNode | None = await node_set.get_or_none(**match_properties)

            if not node:
                raise ValueError(f'Node with properties {match_properties} not found')

            if node:
                for key, value in update_properties.items():
                    setattr(node, key, value)

                await node.save()
