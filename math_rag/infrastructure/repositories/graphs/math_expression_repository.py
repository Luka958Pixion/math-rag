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

    async def breadth_first_search(
        self, start_id: UUID, *, max_depth: int, filter_cb: Callable[[MathExpression], bool] | None
    ) -> list[tuple[UUID, UUID, UUID]]:
        node_set = cast(AsyncNodeSet, self.target_node_cls.nodes)
        start_node = cast(MathExpressionNode, await node_set.get_or_none(uid=start_id))

        if not start_node:
            return []

        visited: set[str] = {start_node.uid}
        visited_pairs: set[tuple[UUID, UUID, UUID]] = set()
        queue: deque[tuple[MathExpressionNode, int]] = deque([(start_node, 0)])
        triples: list[tuple[UUID, UUID, UUID]] = []

        while queue:
            node, depth = queue.popleft()
            if depth >= max_depth:
                continue

            out_mgr = cast(AsyncRelationshipManager, node.related_to)
            in_mgr = cast(AsyncRelationshipManager, node.related_from)

            out_neighbors = cast(list[MathExpressionNode], await out_mgr.match())
            in_neighbors = cast(list[MathExpressionNode], await in_mgr.match())
            neighbors = out_neighbors + in_neighbors

            for nbr_node in neighbors:
                if nbr_node.uid in visited:
                    continue

                rels: list[MathExpressionRel] = []

                if nbr_node in out_neighbors:
                    rels.extend(await out_mgr.all_relationships(nbr_node))

                if nbr_node in in_neighbors:
                    rels.extend(await in_mgr.all_relationships(nbr_node))

                visited.add(nbr_node.uid)
                queue.append((nbr_node, depth + 1))

                expr = self.mapping_node_cls.to_source(node)
                nbr_expr = self.mapping_node_cls.to_source(nbr_node)

                for rel in rels:
                    rel_expr = self.mapping_rel_cls.to_source(rel)

                    if filter_cb is None or filter_cb(nbr_expr):
                        key = (rel_expr.id, min(expr.id, nbr_expr.id), max(expr.id, nbr_expr.id))

                        # skip duplicates, e.g. (0, x, 1) and (1, x, 0)
                        if key in visited_pairs:
                            continue

                        visited_pairs.add(key)
                        triples.append((expr.id, rel_expr.id, nbr_expr.id))

        return triples
