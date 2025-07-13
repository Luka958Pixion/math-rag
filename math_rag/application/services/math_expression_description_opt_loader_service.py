from logging import getLogger

from more_itertools import unzip

from math_rag.application.assistants import MathExpressionDescriptionOptimizerAssistant
from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDescriptionOptRepository,
    BaseMathExpressionDescriptionRepository,
)
from math_rag.application.base.repositories.embeddings import (
    BaseMathExpressionDescriptionOptRepository as BaseMathExpressionDescriptionOptEmbeddingRepository,
)
from math_rag.application.base.services import (
    BaseMathExpressionDescriptionOptLoaderService,
)
from math_rag.application.embedders import DefaultEmbedder
from math_rag.application.models.assistants.inputs import (
    MathExpressionDescriptionOptimizer as AssistantInput,
)
from math_rag.application.models.embedders import EmbedderInput
from math_rag.application.utils import InputCreatorUtil
from math_rag.core.models import (
    MathExpressionDescriptionOpt,
    MathExpressionIndex,
)


logger = getLogger(__name__)


class MathExpressionDescriptionOptLoaderService(BaseMathExpressionDescriptionOptLoaderService):
    def __init__(
        self,
        default_embedder: DefaultEmbedder,
        math_expression_description_optimizer_assistant: MathExpressionDescriptionOptimizerAssistant,
        math_expression_description_repository: BaseMathExpressionDescriptionRepository,
        math_expression_description_opt_repository: BaseMathExpressionDescriptionOptRepository,
        math_expression_description_opt_embedding_repository: BaseMathExpressionDescriptionOptEmbeddingRepository,
    ):
        self.default_embedder = default_embedder
        self.math_expression_description_optimizer_assistant = (
            math_expression_description_optimizer_assistant
        )
        self.math_expression_description_repository = math_expression_description_repository
        self.math_expression_description_opt_repository = math_expression_description_opt_repository
        self.math_expression_description_opt_embedding_repository = (
            math_expression_description_opt_embedding_repository
        )

    async def load_for_index(self, index: MathExpressionIndex):
        index_filter = dict(math_expression_index_id=index.id)

        # math expressions descriptions
        math_expression_descriptions = await self.math_expression_description_repository.find_many(
            filter=index_filter
        )

        # math expression descriptions opt
        inputs, input_id_to_math_expression_description = InputCreatorUtil.create(
            math_expression_descriptions, lambda x: AssistantInput(description=x.text)
        )
        outputs = await self.math_expression_description_optimizer_assistant.concurrent_assist(
            inputs
        )
        math_expression_descriptions_opt = [
            MathExpressionDescriptionOpt(
                math_expression_id=input_id_to_math_expression_description[
                    output.input_id
                ].math_expression_id,
                math_expression_description_id=input_id_to_math_expression_description[
                    output.input_id
                ].id,
                math_expression_index_id=index.id,
                text=output.description,
            )
            for output in outputs
        ]

        # math expression description opt embeddings
        inputs, input_id_to_item = InputCreatorUtil.create(
            math_expression_descriptions_opt, lambda x: EmbedderInput(text=x.text)
        )
        outputs = await self.default_embedder.concurrent_embed(inputs)
        descriptions, embeddings = unzip(
            (input_id_to_item[output.input_id], output.embedding) for output in outputs
        )
        descriptions, embeddings = list(descriptions), list(embeddings)

        await self.math_expression_description_opt_repository.insert_many(descriptions)
        await self.math_expression_description_opt_embedding_repository.upsert_many(
            descriptions, embeddings
        )
        logger.info(
            f'{self.__class__.__name__} loaded {len(descriptions)} math expression descriptions opt'
        )
