from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import Prompt
from mcp.server.fastmcp.prompts.base import Message, PromptArgument
from mcp.types import TextContent

from math_rag.mcp.base import BasePrompt


class SummarizeTextPrompt(BasePrompt):
    def summarize_text(self, text: str) -> list[Message]:
        return [
            Message(
                role='user', content=[TextContent(text=f'Can you please summarize this: {text}?')]
            )
        ]

    def add(self, mcp: FastMCP):
        mcp.add_prompt(
            Prompt(
                name='summarize',
                description='Summarizes the given text.',
                arguments=[
                    PromptArgument(name='text', description='Text to summarize.', required=True)
                ],
                fn=self.summarize_text,
            )
        )
