from mcp.server.fastmcp.prompts import Prompt
from mcp.server.fastmcp.prompts.base import PromptArgument


def summarize_text(text: str) -> str:
    return f'Summary: {text[:50]}...'


PROMPT = Prompt(
    name='summarize',
    description='Summarizes the given text.',
    arguments=[PromptArgument(name='text', description='Text to summarize.', required=True)],
    fn=summarize_text,
)
