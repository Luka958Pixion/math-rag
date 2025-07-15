import json

from agents.tool import FunctionTool, ToolContext
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel, ConfigDict, Field

from math_rag.application.base.clients import BaseJupyterClient
from math_rag.application.containers import ApplicationContainer


class ExecuteCodeParams(BaseModel):
    code: str = Field(
        ...,
        description='The Python code to execute in an isolated Jupyter environment.',
    )

    model_config = ConfigDict(extra='forbid')


@inject
async def _invoke_execute_code(
    _: ToolContext,
    args_json: str,
    jupyter_client: BaseJupyterClient = Provide[ApplicationContainer.jupyter_client],
) -> str:
    try:
        params = json.loads(args_json)
        result = await jupyter_client.execute_code(user_id='0', code=params['code'])
        # result = await _execute_code(params['code'])

        return result.model_dump_json()

    # any exception becomes feedback to the LLM
    except Exception as e:
        return str(e)


TOOL_DESCRIPTION = """
Execute Python code in an isolated Jupyter environment with numpy 2.2.3 and pandas 2.2.3 installed.
Returns the code execution result with output or error.
"""

execute_code_tool = FunctionTool(
    name='execute_code',
    description=TOOL_DESCRIPTION,
    params_json_schema=ExecuteCodeParams.model_json_schema(),
    on_invoke_tool=_invoke_execute_code,
    strict_json_schema=True,
)
