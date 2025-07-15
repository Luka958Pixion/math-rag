from collections import deque
from typing import Callable, cast
from uuid import UUID

from neomodel import AsyncNodeSet, AsyncRelationshipManager

from math_rag.application.base.repositories.graphs import BaseMathExpressionRepository
from math_rag.core.models import MathExpression, MathExpressionRelationship
from math_rag.infrastructure.mappings.graphs import (
    MathExpressionMapping,
    MathExpressionRelationshipMapping,
)
from math_rag.infrastructure.models.graphs import MathExpressionNode, MathExpressionRel

from .graph_repository import GraphRepository


class MathExpressionRepository(
    BaseMathExpressionRepository,
    GraphRepository[
        MathExpression,
        MathExpressionRelationship,
        MathExpressionNode,
        MathExpressionRel,
        MathExpressionMapping,
        MathExpressionRelationshipMapping,
    ],
):
    def __init__(self):
        super().__init__(
            rel_field='related_to',
            source_node_id_field='math_expression_source_id',
            target_node_id_field='math_expression_target_id',
        )

    async def bfs(
        self, start_id: UUID, max_depth: int, filter_fn: Callable[[MathExpression], bool] | None
    ) -> list[tuple[MathExpression, MathExpressionRelationship, MathExpression]]:
        node_set = cast(AsyncNodeSet, self.target_node_cls.nodes)
        start_node = cast(MathExpressionNode, await node_set.get_or_none(uid=start_id))

        if not start_node:
            return []

        visited: set[str] = {start_node.uid}
        triples: list[tuple[MathExpression, MathExpressionRelationship, MathExpression]] = []
        queue: deque[tuple[MathExpressionNode, int]] = deque([(start_node, 0)])

        while queue:
            node, depth = queue.popleft()
            if depth >= max_depth:
                continue

            out_mgr = cast(AsyncRelationshipManager, node.related_to)
            in_mgr = cast(AsyncRelationshipManager, node.related_from)

            out_neighbors = cast(list[MathExpressionNode], await out_mgr.match())
            in_neighbors = cast(list[MathExpressionNode], await in_mgr.match())

            neighbors = out_neighbors + in_neighbors

            for nbr in neighbors:
                if nbr.uid in visited:
                    continue

                rels: list[MathExpressionRel] = []

                if nbr in out_neighbors:
                    rels.extend(await out_mgr.all_relationships(nbr))

                if nbr in in_neighbors:
                    rels.extend(await in_mgr.all_relationships(nbr))

                visited.add(nbr.uid)
                queue.append((nbr, depth + 1))

                src_expr = self.mapping_node_cls.to_source(node)
                tgt_expr = self.mapping_node_cls.to_source(nbr)

                for rel in rels:
                    rel_expr = self.mapping_rel_cls.to_source(rel)

                    if filter_fn is None or filter_fn(tgt_expr):
                        triples.append((src_expr, rel_expr, tgt_expr))

        return triples
