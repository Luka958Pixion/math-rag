from logging import getLogger
from uuid import UUID

from math_rag.application.assistants import MathExpressionRelationshipDescriptionWriterAssistant
from math_rag.application.base.repositories.documents import (
    BaseMathArticleChunkRepository,
    BaseMathExpressionRelationshipDescriptionRepository,
    BaseMathExpressionRelationshipRepository,
)
from math_rag.application.base.services import (
    BaseMathExpressionRelationshipDescriptionLoaderService,
)
from math_rag.application.models.assistants.inputs import (
    MathExpressionRelationshipDescriptionWriter as AssistantInput,
)
from math_rag.core.models import MathExpressionIndex, MathExpressionRelationshipDescription


logger = getLogger(__name__)


class MathExpressionRelationshipDescriptionLoaderService(
    BaseMathExpressionRelationshipDescriptionLoaderService
):
    def __init__(
        self,
        math_expression_relationship_description_writer_assistant: MathExpressionRelationshipDescriptionWriterAssistant,
        math_article_chunk_repository: BaseMathArticleChunkRepository,
        math_expression_relationship_description_repository: BaseMathExpressionRelationshipDescriptionRepository,
        math_expression_relationship_repository: BaseMathExpressionRelationshipRepository,
    ):
        self.math_expression_relationship_description_writer_assistant = (
            math_expression_relationship_description_writer_assistant
        )
        self.math_article_chunk_repository = math_article_chunk_repository
        self.math_expression_relationship_description_repository = (
            math_expression_relationship_description_repository
        )
        self.math_expression_relationship_repository = math_expression_relationship_repository

    async def load_for_index(self, index: MathExpressionIndex):
        index_filter = dict(math_expression_index_id=index.id)

        # math expression relationships
        math_expression_relationships = (
            await self.math_expression_relationship_repository.find_many(filter=index_filter)
        )

        # math article chunks
        math_article_chunk_ids = [
            math_expression_relationship.math_article_chunk_id
            for math_expression_relationship in math_expression_relationships
        ]
        math_article_chunks = await self.math_article_chunk_repository.find_many(
            filter=dict(id=math_article_chunk_ids)
        )

        # math expression relationship description
        inputs: list[AssistantInput] = []
        input_id_to_math_expression_relationship_id: dict[UUID, UUID] = {}

        for math_article_chunk, math_expression_relationship in zip(
            math_article_chunks, math_expression_relationships
        ):
            input = AssistantInput(
                chunk=math_article_chunk.text,
                source=math_expression_relationship.math_expression_source_index,
                target=math_expression_relationship.math_expression_target_index,
            )
            inputs.append(input)
            input_id_to_math_expression_relationship_id[input.id] = math_expression_relationship.id

        outputs = (
            await self.math_expression_relationship_description_writer_assistant.concurrent_assist(
                inputs
            )
        )
        descriptions = [
            MathExpressionRelationshipDescription(
                math_expression_index_id=index.id,
                math_expression_relationship_id=input_id_to_math_expression_relationship_id[
                    output.input_id
                ],
                text=output.description,
            )
            for output in outputs
        ]
        await self.math_expression_relationship_description_repository.insert_many(descriptions)

        logger.info(f'{self.__class__.__name__} loaded {len(descriptions)} items')
