from typing import Any, Generic, cast

from neo4j import AsyncGraphDatabase
from neomodel import (
    AsyncNodeSet,
    AsyncRelationshipManager,
    AsyncStructuredNode,
    adb,
)

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

    async def close(self):
        await adb.close_connection()

    async def insert_one_node(self, item: SourceNodeType):
        node = self.mapping_node_cls.to_target(item)

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

        node_set = cast(AsyncNodeSet, self.target_node_cls.nodes)
        node = await node_set.get_or_none(**filter)

        if not node:
            return None

        return self.mapping_node_cls.to_source(node)

    async def find_many_nodes(self, *, filter: dict[str, Any]) -> list[SourceNodeType]:
        if 'id' in filter:
            filter['uid'] = filter.pop('id')
        for key, value in list(filter.items()):
            if isinstance(value, list):
                filter[f'{key}__in'] = filter.pop(key)

        node_set = cast(AsyncNodeSet, self.target_node_cls.nodes)
        nodes = await node_set.filter(**filter).all()
        return [self.mapping_node_cls.to_source(n) for n in nodes]

    async def update_one_node(self, *, filter: dict[str, Any], update: dict[str, Any]):
        if 'id' in filter:
            filter['uid'] = filter.pop('id')

        node_set = cast(AsyncNodeSet, self.target_node_cls.nodes)
        node = await node_set.get_or_none(**filter)

        if not node:
            raise ValueError(f'Node with filter {filter} not found')

        for key, value in update.items():
            setattr(node, key, value)

        async with adb.transaction:
            node = cast(AsyncStructuredNode, node)
            await node.save()

    async def insert_one_rel(self, rel: SourceRelType):
        rel_obj = self.mapping_rel_cls.to_target(rel)
        source_node_id = getattr(rel_obj, self.source_node_id_field)
        target_node_id = getattr(rel_obj, self.target_node_id_field)

        props = {
            key: value
            for key, value in rel_obj.__properties__.items()
            if key != 'uid' and value is not None
        }

        node_set = cast(AsyncNodeSet, self.target_node_cls.nodes)
        source_node = await node_set.get(uid=source_node_id)
        node_set = cast(AsyncNodeSet, self.target_node_cls.nodes)
        target_node = await node_set.get(uid=target_node_id)

        async with adb.transaction:
            rel_manager = cast(AsyncRelationshipManager, getattr(source_node, self.rel_field))
            await rel_manager.connect(target_node, properties=props)

    async def insert_many_rels(self, rels: list[SourceRelType]):
        if not rels:
            return

        async with adb.transaction:
            for rel in rels:
                rel_obj = self.mapping_rel_cls.to_target(rel)
                properties = {
                    key: value
                    for key, value in rel_obj.__properties__.items()
                    if key != 'uid' and value is not None
                }

                node_set = cast(AsyncNodeSet, self.target_node_cls.nodes)
                source_node_id = getattr(rel_obj, self.source_node_id_field)
                source_node = await node_set.get(uid=source_node_id)

                node_set = cast(AsyncNodeSet, self.target_node_cls.nodes)
                target_node_id = getattr(rel_obj, self.target_node_id_field)
                target_node = await node_set.get(uid=target_node_id)

                rel_manager = cast(AsyncRelationshipManager, getattr(source_node, self.rel_field))
                await rel_manager.connect(target_node, properties=properties)

    async def find_many_rels(self, *, filter: dict[str, Any]) -> list[SourceRelType]:
        if 'id' in filter:
            filter['uid'] = filter.pop('id')

        node_set = cast(AsyncNodeSet, self.target_node_cls.nodes)
        node = await node_set.get_or_none(**filter)

        if not node:
            return []

        rel_manager = cast(AsyncRelationshipManager, getattr(node, self.rel_field))
        rels = await rel_manager.all_relationships(node)
        return [self.mapping_rel_cls.to_source(rel) for rel in rels]

    async def clear(self):
        await adb.clear_neo4j_database(clear_constraints=True, clear_indexes=True)
