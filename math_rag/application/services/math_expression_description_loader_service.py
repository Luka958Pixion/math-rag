from logging import getLogger
from uuid import UUID

from math_rag.application.assistants import MathExpressionDescriptionWriterAssistant
from math_rag.application.base.repositories.documents import (
    BaseMathExpressionContextRepository,
    BaseMathExpressionDescriptionRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.services import (
    BaseMathArticleParserService,
    BaseMathExpressionDescriptionLoaderService,
)
from math_rag.application.models.assistants.inputs import (
    MathExpressionDescriptionWriter as AssistantInput,
)
from math_rag.core.models import (
    MathExpressionDescription,
    MathExpressionIndex,
)
from math_rag.infrastructure.constants.services import MATH_TEMPLATE


logger = getLogger(__name__)


class MathExpressionDescriptionLoaderService(BaseMathExpressionDescriptionLoaderService):
    def __init__(
        self,
        math_expression_description_writer_assistant: MathExpressionDescriptionWriterAssistant,
        math_article_parser_service: BaseMathArticleParserService,
        math_expression_repository: BaseMathExpressionRepository,
        math_expression_context_repository: BaseMathExpressionContextRepository,
        math_expression_description_repository: BaseMathExpressionDescriptionRepository,
    ):
        self.math_expression_description_writer_assistant = (
            math_expression_description_writer_assistant
        )
        self.math_article_parser_service = math_article_parser_service
        self.math_expression_repository = math_expression_repository
        self.math_expression_context_repository = math_expression_context_repository
        self.math_expression_description_repository = math_expression_description_repository

    async def load_for_index(self, index: MathExpressionIndex):
        index_filter = dict(math_expression_index_id=index.id)

        # math expressions
        math_expressions = await self.math_expression_repository.find_many(filter=index_filter)

        # math expression contexts
        math_expression_contexts = await self.math_expression_context_repository.find_many(
            filter=index_filter
        )

        # math expression descriptions
        inputs: list[AssistantInput] = []
        input_id_to_math_expression_id: dict[UUID, UUID] = {}

        for math_expression, math_expression_context in zip(
            math_expressions, math_expression_contexts
        ):
            input = AssistantInput(
                katex=MATH_TEMPLATE.format(
                    katex=math_expression.katex, index=math_expression.index
                ),
                context=math_expression_context.text,
            )
            inputs.append(input)
            input_id_to_math_expression_id[input.id] = math_expression.id

        outputs = await self.math_expression_description_writer_assistant.concurrent_assist(inputs)
        math_expression_descriptions = [
            MathExpressionDescription(
                math_expression_index_id=index.id,
                math_expression_id=input_id_to_math_expression_id[output.input_id],
                text=output.description,
            )
            for output in outputs
        ]
        await self.math_expression_description_repository.insert_many(math_expression_descriptions)
        logger.info(
            f'{self.__class__.__name__} loaded {len(math_expression_descriptions)} math expression descriptions'
        )
