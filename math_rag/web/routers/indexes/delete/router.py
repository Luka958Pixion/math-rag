from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from math_rag.application.base.repositories.documents import (
    BaseMathArticleChunkRepository,
    BaseMathExpressionContextRepository,
    BaseMathExpressionDescriptionOptRepository,
    BaseMathExpressionDescriptionRepository,
    BaseMathExpressionGroupRepository,
    BaseMathExpressionIndexRepository,
    BaseMathExpressionRelationshipDescriptionRepository,
    BaseMathExpressionRelationshipRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.repositories.embeddings import (
    BaseMathExpressionDescriptionOptRepository as BaseMathExpressionDescriptionOptEmbeddingRepository,
)
from math_rag.application.base.repositories.graphs import (
    BaseMathExpressionGroupRepository as BaseMathExpressionGroupGraphRepository,
    BaseMathExpressionRepository as BaseMathExpressionGraphRepository,
)
from math_rag.application.containers import ApplicationContainer


logger = getLogger(__name__)
router = APIRouter()


@router.delete('/indexes/math-expressions/', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_math_expression_indexes(
    # documents
    math_article_chunk_repository: BaseMathArticleChunkRepository = Depends(
        Provide[ApplicationContainer.math_article_chunk_repository]
    ),
    math_expression_context_repository: BaseMathExpressionContextRepository = Depends(
        Provide[ApplicationContainer.math_expression_context_repository]
    ),
    math_expression_description_opt_repository: BaseMathExpressionDescriptionOptRepository = Depends(
        Provide[ApplicationContainer.math_expression_description_opt_repository]
    ),
    math_expression_description_repository: BaseMathExpressionDescriptionRepository = Depends(
        Provide[ApplicationContainer.math_expression_description_repository]
    ),
    math_expression_group_repository: BaseMathExpressionGroupRepository = Depends(
        Provide[ApplicationContainer.math_expression_group_repository]
    ),
    math_expression_index_repository: BaseMathExpressionIndexRepository = Depends(
        Provide[ApplicationContainer.math_expression_index_repository]
    ),
    math_expression_relationship_description_repository: BaseMathExpressionRelationshipDescriptionRepository = Depends(
        Provide[ApplicationContainer.math_expression_relationship_description_repository]
    ),
    math_expression_relationship_repository: BaseMathExpressionRelationshipRepository = Depends(
        Provide[ApplicationContainer.math_expression_relationship_repository]
    ),
    math_expression_repository: BaseMathExpressionRepository = Depends(
        Provide[ApplicationContainer.math_expression_repository]
    ),
    # embeddings
    math_expression_description_opt_embedding_repository: BaseMathExpressionDescriptionOptEmbeddingRepository = Depends(
        Provide[ApplicationContainer.math_expression_description_opt_embedding_repository]
    ),
    # graphs
    math_expression_group_graph_repository: BaseMathExpressionGroupGraphRepository = Depends(
        Provide[ApplicationContainer.math_expression_group_graph_repository]
    ),
    math_expression_graph_repository: BaseMathExpressionGraphRepository = Depends(
        Provide[ApplicationContainer.math_expression_graph_repository]
    ),
):
    math_expression_indexes = await math_expression_index_repository.find_many(filter=None)
    math_expression_index_ids = [x.id for x in math_expression_indexes]

    # documents
    await math_article_chunk_repository.clear()
    await math_expression_context_repository.clear()
    await math_expression_description_opt_repository.clear()
    await math_expression_description_repository.clear()
    await math_expression_group_repository.clear()
    await math_expression_index_repository.clear()
    await math_expression_relationship_description_repository.clear()
    await math_expression_relationship_repository.clear()
    await math_expression_repository.delete_many(
        filter=dict(math_expression_index_id=math_expression_index_ids)
    )

    # embeddings
    await math_expression_description_opt_embedding_repository.clear()

    # graphs
    await math_expression_group_graph_repository.clear()
    await math_expression_graph_repository.clear()
