import json

from agents.tool import FunctionTool, ToolContext
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel, ConfigDict, Field

from math_rag.application.containers import ApplicationContainer


class SearchGraphParams(BaseModel):
    katex: str = Field(
        ...,
        description='TODO',
    )

    model_config = ConfigDict(extra='forbid')


@inject
async def _invoke_search_graph(
    _: ToolContext,
    args_json: str,
    # katex_client: BaseKatexClient = Provide[ApplicationContainer.katex_client], # TODO
) -> str:
    try:
        params = json.loads(args_json)
        result = ...
        # result = await katex_client.validate(katex=params['katex']) # TODO

        return result.model_dump_json()

    # any exception becomes feedback to the LLM
    except Exception as e:
        return str(e)


TOOL_DESCRIPTION = """
Search a knowledge graph.
Returns the ....
"""  # TODO

search_graph_tool = FunctionTool(
    name='search_graph',
    description=TOOL_DESCRIPTION,
    params_json_schema=SearchGraphParams.model_json_schema(),
    on_invoke_tool=_invoke_search_graph,
    strict_json_schema=True,
)
