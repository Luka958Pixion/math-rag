import pytest

from math_rag.application.models.assistants import (
    KatexCorrectorAssistantInput,
    KatexCorrectorAssistantOutput,
)
from math_rag.infrastructure.containers import InfrastructureContainer


@pytest.mark.asyncio
async def test_assist(infrastructure_container: InfrastructureContainer):
    # arrange
    katex_corrector_assistant = infrastructure_container.katex_corrector_assistant()
    input = KatexCorrectorAssistantInput(
        katex=r'd\omega = \theta \w \omega',
        error=(
            r'KaTeX parse error: Undefined control sequence: '
            r'\w at position 18: …omega = \theta \̲w̲ ̲\omega'
        ),
    )

    # act
    output = await katex_corrector_assistant.assist(input)

    # assert
    type(output) == KatexCorrectorAssistantOutput
