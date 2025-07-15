import json

from typing import Annotated
from uuid import UUID

from agents.tool import FunctionTool, ToolContext
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel, ConfigDict, Field

from math_rag.application.base.services import (
    BaseMathExpressionIndexSearcherService,
    BaseMathExpressionRelationshipSerializerService,
)
from math_rag.application.containers import ApplicationContainer


class SearchGraphParams(BaseModel):
    query: str = Field(..., description='Precise query for searching the knowledge graph.')
    query_limit: Annotated[int, Field(ge=1, le=4)] = Field(
        ..., description='Number of starting nodes from which to search.'
    )
    limit: Annotated[int, Field(ge=1, le=8)] = Field(
        ..., description='Total number of returned results.'
    )

    model_config = ConfigDict(extra='forbid')


@inject
async def _invoke_search_graph(
    _: ToolContext,
    args_json: str,
    math_expression_index_id: UUID,
    math_expression_index_searcher_service: BaseMathExpressionIndexSearcherService = Provide[
        ApplicationContainer.math_expression_index_searcher_service
    ],
    math_expression_relationship_serializer_service: BaseMathExpressionRelationshipSerializerService = Provide[
        ApplicationContainer.math_expression_relationship_serializer_service
    ],
) -> str:
    try:
        params = json.loads(args_json)
        math_expression_relationship_ids = await math_expression_index_searcher_service.search(
            math_expression_index_id,
            params['query'],
            query_limit=params['query_limit'],
            limit=params['limit'],
        )
        result = await math_expression_relationship_serializer_service.serialize(
            math_expression_relationship_ids
        )

        return result

    # any exception becomes feedback to the LLM
    except Exception as e:
        return str(e)


TOOL_DESCRIPTION = """
Search a knowledge graph to solve the math problem.
Returns the serialized JSON list of (source_entity, target_entity, relationship) entries.
"""

search_graph_tool = FunctionTool(
    name='search_graph',
    description=TOOL_DESCRIPTION,
    params_json_schema=SearchGraphParams.model_json_schema(),
    on_invoke_tool=_invoke_search_graph,
    strict_json_schema=True,
)
