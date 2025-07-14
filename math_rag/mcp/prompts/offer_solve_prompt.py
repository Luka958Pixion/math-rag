from mcp.server.fastmcp.prompts import Prompt
from mcp.server.fastmcp.prompts.base import Message
from mcp.types import TextContent

from math_rag.mcp.base import BasePrompt


class OfferSolvePrompt(BasePrompt):
    def offer_solve(self, _) -> list[Message]:
        return [
            Message(
                role='assistant',
                content=[
                    TextContent(
                        text=(
                            'This service provides literature-based math problem solving. '
                            'Please upload a single PDF document for indexing. '
                            'You will be notified when indexing completes.'
                        )
                    )
                ],
            )
        ]

    def add(self, mcp):
        mcp.add_prompt(
            Prompt(
                name='offer_solve',
                description='Introduce the literature indexing step.',
                arguments=[],
                fn=self.offer_solve,
            )
        )
