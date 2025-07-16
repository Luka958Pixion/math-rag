from functools import partial
from uuid import UUID

from agents import Agent, ModelSettings


class MathProblemSolverAgent(Agent):
    def __init__(self, math_expression_index_id: UUID):
        from .tools import execute_code_tool, search_graph_tool

        search_graph_tool.on_invoke_tool = partial(
            search_graph_tool.on_invoke_tool,
            math_expression_index_id=math_expression_index_id,
        )

        super().__init__(
            name='MathProblemSolverAgent',
            model='o4-mini',
            model_settings=ModelSettings(tool_choice='required'),
            instructions='You are an assistant for solving math problems.',
            tools=[execute_code_tool, search_graph_tool],
            reset_tool_choice=True,
        )


MATH_PROBLEM_SOLVER_INPUT_TEMPLATE = """
Solve the given math problem step-by-step by following steps:
1. break the problem into smaller pieces
2. write a `query` to search the knowledge graph
2. call `search_graph_tool` to search the knowledge graph with that `query` (you MUST call `search_graph_tool` at least once)
3. after each `search_graph_tool` call, check if the search returned useful info
4. if you did not get useful info, increase search limits when calling `search_graph_tool` or rewrite query
5. call `execute_code_tool` to execute Python code where appropriate
6. check if the code executed successufully, then see if you need more tool calls or debug
7. if you haven't solved the problem yet, iterate until you get the solution, order of steps is not 100%% strict
8. include all relevant formulas and detailed reasoning in the final answer, but do NOT show any code

Your task:
{text}
"""
