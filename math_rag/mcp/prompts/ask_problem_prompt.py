from mcp.server.fastmcp.prompts import Prompt
from mcp.server.fastmcp.prompts.base import Message
from mcp.types import TextContent

from math_rag.mcp.base import BasePrompt


class AskProblemPrompt(BasePrompt):
    def ask_problem(self, _) -> list[Message]:
        return [
            Message(
                role='assistant',
                content=[
                    TextContent(
                        text=(
                            'Indexing has completed. Please submit your math problem '
                            'by typing it or uploading a .txt, .pdf, or image file.'
                        )
                    )
                ],
            )
        ]

    def add(self, mcp):
        mcp.add_prompt(
            Prompt(
                name='ask_problem',
                description='Prompt user to submit problem after indexing.',
                arguments=[],
                fn=self.ask_problem,
            )
        )
