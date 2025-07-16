# math_rag/mcp/prompts/offer_solve.py
from mcp.server.fastmcp import Context
from mcp.server.fastmcp.prompts import Prompt
from mcp.server.fastmcp.prompts.base import Message, PromptArgument
from mcp.types import TextContent

from math_rag.mcp.base import BasePrompt


class OfferSolvePrompt(BasePrompt):
    def offer_solve(self, _: Context) -> list[Message]:
        # session = _.session
        # session['intro_shown'] = True
        return [
            Message(
                role='assistant',
                content=[
                    TextContent(text='Welcome! I can help you solve a math problem, lets begin.')
                ],
            )
        ]

    def add(self, mcp):
        mcp.add_prompt(
            Prompt(
                name='offer_solve',
                description='Introduces the service once at session start.',
                arguments=[PromptArgument(name='ctx')],
                fn=self.offer_solve,
            )
        )
