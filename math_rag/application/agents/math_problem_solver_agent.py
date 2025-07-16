from functools import partial
from uuid import UUID

from agents import Agent

from math_rag.application.agents.tools import execute_code_tool, search_graph_tool


class MathProblemSolverAgent(Agent):
    def __init__(self, math_expression_index_id: UUID):
        search_graph_tool.on_invoke_tool = partial(
            search_graph_tool.on_invoke_tool,
            math_expression_index_id=math_expression_index_id,
        )

        super().__init__(
            name='MathProblemSolverAgent',
            model='o4-mini',
            instructions='You are an assistant for solving math problems.',
            tools=[execute_code_tool],
        )


MATH_PROBLEM_SOLVER_INPUT_TEMPLATE = """
Solve the given math problem step-by-step by following steps:
1. call search_graph_tool to search the knowledge graph  where appropriate
2. after each search_graph_tool call, check if the search returned useful info
3. if you did not get useful info, increase search limits when calling search_graph_tool or rewrite query
4. call execute_code_tool to execute Python code where appropriate
5. check if the code executed successufully, then see if you need more tool calls or debug
6. if you haven't solved the problem yet, iterate until you get the solution, order of steps is not 100%% strict
5. include all relevant formulas and detailed reasoning in the final answer, but do NOT show any code

Your task:
{text}
"""
