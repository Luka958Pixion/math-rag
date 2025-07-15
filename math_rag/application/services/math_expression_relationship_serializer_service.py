import json

from uuid import UUID

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDescriptionRepository,
    BaseMathExpressionRelationshipDescriptionRepository,
    BaseMathExpressionRelationshipRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.services import BaseMathExpressionRelationshipSerializerService


class MathExpressionRelationshipSerializerService(BaseMathExpressionRelationshipSerializerService):
    def __init__(
        self,
        math_expression_description_repository: BaseMathExpressionDescriptionRepository,
        math_expression_relationship_description_repository: BaseMathExpressionRelationshipDescriptionRepository,
        math_expression_relationship_repository: BaseMathExpressionRelationshipRepository,
        math_expression_repository: BaseMathExpressionRepository,
    ):
        self.math_expression_description_repository = math_expression_description_repository
        self.math_expression_relationship_description_repository = (
            math_expression_relationship_description_repository
        )
        self.math_expression_relationship_repository = math_expression_relationship_repository
        self.math_expression_repository = math_expression_repository

    async def serialize(self, math_expression_relationship_ids: list[UUID]) -> str:
        if not math_expression_relationship_ids:
            return str()

        relationships = await self.math_expression_relationship_repository.find_many(
            filter=dict(id=math_expression_relationship_ids)
        )
        sorted_relationships = sorted(
            relationships,
            key=lambda rel: (rel.math_expression_source_index, rel.math_expression_target_index),
        )

        math_expression_source_ids = [rel.math_expression_source_id for rel in sorted_relationships]
        source_expressions = await self.math_expression_repository.find_many(
            filter=dict(id=math_expression_source_ids)
        )
        source_descriptions = await self.math_expression_description_repository.find_many(
            filter=dict(math_expression_id=math_expression_source_ids)
        )

        math_expression_target_ids = [rel.math_expression_target_id for rel in sorted_relationships]
        target_expressions = await self.math_expression_repository.find_many(
            filter=dict(id=math_expression_target_ids)
        )
        target_descriptions = await self.math_expression_description_repository.find_many(
            filter=dict(math_expression_id=math_expression_target_ids)
        )

        sorted_relationship_ids = [rel.id for rel in sorted_relationships]
        relationship_descriptions = (
            await self.math_expression_relationship_description_repository.find_many(
                filter=dict(math_expression_relationship_id=sorted_relationship_ids)
            )
        )

        results = [
            dict(
                source_entity=dict(katex=src_expr.katex, description=src_desc.text),
                target_entity=dict(katex=tgt_expr.katex, description=tgt_desc.text),
                relationship=rel_desc.text,
            )
            for src_expr, src_desc, tgt_expr, tgt_desc, rel_desc in zip(
                source_expressions,
                source_descriptions,
                target_expressions,
                target_descriptions,
                relationship_descriptions,
            )
        ]

        return json.dumps(results)
