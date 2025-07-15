from collections import Counter
from uuid import UUID

from math_rag.application.base.repositories.documents import BaseMathExpressionRepository
from math_rag.application.base.repositories.embeddings import (
    BaseMathExpressionDescriptionOptRepository as BaseMathExpressionDescriptionOptEmbeddingRepository,
)
from math_rag.application.base.repositories.graphs import (
    BaseMathExpressionRepository as BaseMathExpressionGraphRepository,
)
from math_rag.application.base.services import BaseMathExpressionIndexSearcherService
from math_rag.application.embedders import DefaultEmbedder
from math_rag.application.models.embedders import EmbedderInput


class MathExpressionIndexSearcherService(BaseMathExpressionIndexSearcherService):
    def __init__(
        self,
        default_embedder: DefaultEmbedder,
        math_expression_description_opt_embedding_repository: BaseMathExpressionDescriptionOptEmbeddingRepository,
        math_expression_graph_repository: BaseMathExpressionGraphRepository,
        math_expression_repository: BaseMathExpressionRepository,
    ):
        self.default_embedder = default_embedder
        self.embedding_repository = math_expression_description_opt_embedding_repository
        self.math_expression_graph_repository = math_expression_graph_repository
        self.math_expression_repository = math_expression_repository

    def _has_duplicates(self, triples: list[tuple[UUID, UUID, UUID]]) -> bool:
        visited_triples: set[tuple[UUID, frozenset[UUID]]] = set()

        for src, rel, tgt in triples:
            key = (rel, frozenset({src, tgt}))
            if key in visited_triples:
                return True

            visited_triples.add(key)

        return False

    async def search(
        self,
        index_id: UUID,
        query: str,
        *,
        query_limit: int,
        limit: int,
    ) -> list[UUID]:
        # search optimized math expression descriptions
        input = EmbedderInput(text=query)
        output = await self.default_embedder.embed(input)

        if not output:
            raise ValueError()

        descriptions = await self.embedding_repository.search(
            output.embedding, filter=dict(math_expression_index_id=index_id), limit=query_limit
        )

        # math expressions
        math_expression_ids = [description.math_expression_id for description in descriptions]
        math_expressions = await self.math_expression_repository.find_many(
            filter=dict(id=math_expression_ids)
        )

        # math expression groups
        group_ids = [
            math_expression.math_expression_group_id for math_expression in math_expressions
        ]

        # (expression, relationship, expression)
        triples: list[tuple[UUID, UUID, UUID]] = []

        for group_id in group_ids:
            if not group_id:
                continue

            # groups are distinct, and so are the expanded math expressions
            math_expressions_expanded = await self.math_expression_repository.find_many(
                filter=dict(math_expression_group_id=group_id)
            )

            for math_expression in math_expressions_expanded:
                next_triples = await self.math_expression_graph_repository.breadth_first_search(
                    start_id=math_expression.id, max_depth=2, filter_cb=None
                )

                if self._has_duplicates(next_triples):
                    raise ValueError()

                # skip duplicates, e.g. (0, x, 1) and (1, x, 0)
                for src, rel, tgt in next_triples:
                    is_duplicate = any(
                        rel == existing_rel and {src, tgt} == {existing_src, existing_dst}
                        for existing_src, existing_rel, existing_dst in triples
                    )

                    if not is_duplicate:
                        triples.append((src, rel, tgt))

        if self._has_duplicates(triples):
            raise ValueError()

        # count different math expression ids
        counter: Counter[UUID] = Counter()

        for source_id, _, target_id in triples:
            counter[source_id] += 1
            counter[target_id] += 1

        # relationship (triple) with the nodes of higher degree are ranked higher
        triples_sorted = sorted(
            triples,
            key=lambda triple: counter[triple[0]] + counter[triple[2]],
            reverse=True,
        )

        _, math_expression_relationship_ids, _ = map(list, zip(*triples_sorted[:limit]))

        return math_expression_relationship_ids
