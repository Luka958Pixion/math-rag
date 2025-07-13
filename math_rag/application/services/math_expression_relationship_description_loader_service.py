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
        self.assistant = math_expression_relationship_description_writer_assistant
        self.chunk_repo = math_article_chunk_repository
        self.relationship_description_repo = math_expression_relationship_description_repository
        self.relationship_repo = math_expression_relationship_repository

    async def load_for_index(self, index: MathExpressionIndex):
        index_filter = dict(math_expression_index_id=index.id)

        # math expression relationships
        relationships = await self.relationship_repo.find_many(filter=index_filter)

        # math article chunks
        chunk_ids = [relationship.math_article_chunk_id for relationship in relationships]
        chunks = await self.chunk_repo.find_many(filter=dict(id=chunk_ids))

        # math expression relationship description
        inputs: list[AssistantInput] = []
        input_id_to_relationship_id: dict[UUID, UUID] = {}

        for chunk, relationship in zip(chunks, relationships):
            input = AssistantInput(
                chunk=chunk.text,
                source=relationship.math_expression_source_index,
                target=relationship.math_expression_target_index,
            )
            inputs.append(input)
            input_id_to_relationship_id[input.id] = relationship.id

        outputs = await self.assistant.concurrent_assist(inputs)
        descriptions = [
            MathExpressionRelationshipDescription(
                math_expression_index_id=index.id,
                math_expression_relationship_id=input_id_to_relationship_id[output.input_id],
                text=output.description,
            )
            for output in outputs
        ]
        await self.relationship_description_repo.insert_many(descriptions)

        logger.info(f'{self.__class__.__name__} loaded {len(descriptions)} items')
