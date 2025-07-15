import json

from agents.tool import FunctionTool, ToolContext
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel, ConfigDict, Field

from math_rag.application.base.clients import BaseKatexClient
from math_rag.application.containers import ApplicationContainer


class ValidateKatexParams(BaseModel):
    katex: str = Field(
        ...,
        description='The KaTeX to validate.',
    )

    model_config = ConfigDict(extra='forbid')


@inject
async def _invoke_validate_katex(
    _: ToolContext,
    args_json: str,
    katex_client: BaseKatexClient = Provide[ApplicationContainer.katex_client],
) -> str:
    try:
        params = json.loads(args_json)
        result = await katex_client.validate(katex=params['katex'])

        return result.model_dump_json()

    # any exception becomes feedback to the LLM
    except Exception as e:
        return str(e)


TOOL_DESCRIPTION = """
Validate given KaTeX.
Returns the validation result with output or error.
"""

validate_katex_tool = FunctionTool(
    name='validate_katex',
    description=TOOL_DESCRIPTION,
    params_json_schema=ValidateKatexParams.model_json_schema(),
    on_invoke_tool=_invoke_validate_katex,
    strict_json_schema=True,
)
