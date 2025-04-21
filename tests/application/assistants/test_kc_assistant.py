import pytest

from math_rag.application.models.assistants import KCAssistantInput, KCAssistantOutput
from math_rag.infrastructure.containers import InfrastructureContainer


@pytest.mark.asyncio
async def test_assist(infrastructure_container: InfrastructureContainer):
    # arrange
    kc_assistant = infrastructure_container.kc_assistant()
    input = KCAssistantInput(
        katex=r'd\omega = \theta \w \omega',
        error=(
            r'KaTeX parse error: Undefined control sequence: '
            r'\w at position 18: …omega = \theta \̲w̲ ̲\omega'
        ),
    )

    # act
    output = await kc_assistant.assist(input)

    # assert
    type(output) == KCAssistantOutput
