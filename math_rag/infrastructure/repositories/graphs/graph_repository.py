from typing import Any, Generic, cast

from neo4j import AsyncGraphDatabase
from neomodel import AsyncNodeSet, AsyncRelationshipTo, AsyncStructuredNode, adb

from math_rag.application.base.repositories.graphs import BaseGraphRepository
from math_rag.infrastructure.types.repositories.graphs.nodes import (
    MappingNodeType,
    MappingRelType,
    SourceNodeType,
    SourceRelType,
    TargetNodeType,
    TargetRelType,
)
from math_rag.shared.utils import TypeUtil


class GraphRepository(
    BaseGraphRepository[SourceNodeType, SourceRelType],
    Generic[
        SourceNodeType,
        SourceRelType,
        TargetNodeType,
        TargetRelType,
        MappingNodeType,
        MappingRelType,
    ],
):
    def __init__(
        self,
        rel_field: str,
        source_node_id_field: str,
        target_node_id_field: str,
    ):
        args = TypeUtil.get_type_args(self.__class__)
        self.source_node_cls = cast(type[SourceNodeType], args[1][0])
        self.source_rel_cls = cast(type[SourceRelType], args[1][1])
        self.target_node_cls = cast(type[TargetNodeType], args[1][2])
        self.target_rel_cls = cast(type[TargetRelType], args[1][3])
        self.mapping_node_cls = cast(type[MappingNodeType], args[1][4])
        self.mapping_rel_cls = cast(type[MappingRelType], args[1][5])

        self.rel_field = rel_field
        self.source_node_id_field = source_node_id_field
        self.target_node_id_field = target_node_id_field

    @classmethod
    async def create(
        cls,
        uri: str,
        username: str,
        password: str,
    ) -> 'GraphRepository':
        repo = cls()
        driver = AsyncGraphDatabase.driver(uri=uri, auth=(username, password))
        await adb.set_connection(driver=driver)

        return repo

    async def close(self) -> None:
        await adb.close_connection()

    async def insert_one_node(self, item: SourceNodeType):
        node: AsyncStructuredNode = self.mapping_node_cls.to_target(item)

        async with adb.transaction:
            await node.save()

    async def insert_many_nodes(self, items: list[SourceNodeType]):
        nodes = [self.mapping_node_cls.to_target(i) for i in items]

        async with adb.transaction:
            for node in nodes:
                await node.save()

    async def find_one_node(self, *, filter: dict[str, Any]) -> SourceNodeType | None:
        if 'id' in filter:
            filter['uid'] = filter.pop('id')

        node = await self.target_node_cls.nodes.get_or_none(**filter)
        if node is None:
            return None

        return self.mapping_node_cls.to_source(node)

    async def find_many_nodes(self, *, filter: dict[str, Any]) -> list[SourceNodeType]:
        if 'id' in filter:
            filter['uid'] = filter.pop('id')
        for key, value in list(filter.items()):
            if isinstance(value, list):
                filter[f'{key}__in'] = filter.pop(key)
        nodes = await self.target_node_cls.nodes.filter(**filter).all()
        return [self.mapping_node_cls.to_source(n) for n in nodes]

    async def update_one_node(
        self,
        *,
        filter: dict[str, Any],
        update: dict[str, Any],
    ) -> None:
        if 'id' in filter:
            filter['uid'] = filter.pop('id')
        node = await self.target_node_cls.nodes.get_or_none(**filter)
        if node is None:
            raise ValueError(f'Node with filter {filter} not found')
        for key, value in update.items():
            setattr(node, key, value)
        async with adb.transaction:
            await node.save()

    async def insert_one_rel(
        self,
        rel: SourceRelType,
    ) -> None:
        rel_obj = self.mapping_rel_cls.to_target(rel)

        source_id = getattr(rel_obj, self.source_node_id_field)
        target_id = getattr(rel_obj, self.target_node_id_field)

        props = {
            key: value
            for key, value in rel_obj.__properties__.items()
            if key != 'uid' and value is not None
        }

        source_node = await self.target_node_cls.nodes.get(uid=source_id)
        target_node = await self.target_node_cls.nodes.get(uid=target_id)

        async with adb.transaction:
            await getattr(source_node, self.rel_field).connect(target_node, properties=props)

    async def insert_many_rels(
        self,
        rels: list[SourceRelType],
    ) -> None:
        if not rels:
            return

        async with adb.transaction:
            for rel in rels:
                rel_obj = self.mapping_rel_cls.to_target(rel)
                src = getattr(rel_obj, self.source_node_id_field)
                tgt = getattr(rel_obj, self.target_node_id_field)

                props = {
                    k: v for k, v in rel_obj.__properties__.items() if k != 'uid' and v is not None
                }

                source_node = await self.target_node_cls.nodes.get(uid=src)
                target_node = await self.target_node_cls.nodes.get(uid=tgt)
                await getattr(source_node, self.rel_field).connect(target_node, properties=props)

    async def find_many_rels(self, *, anchor_filter: dict[str, Any]) -> list[SourceRelType]:
        if 'id' in anchor_filter:
            anchor_filter['uid'] = anchor_filter.pop('id')
        anchor = await self.target_node_cls.nodes.get_or_none(**anchor_filter)
        if not anchor:
            return []
        rel_objs = await getattr(anchor, self.rel_field).all_relationships(anchor)
        return [self.mapping_rel_cls.to_source(r) for r in rel_objs]

    async def clear(self) -> None:
        await adb.clear_neo4j_database(clear_constraints=True, clear_indexes=True)
