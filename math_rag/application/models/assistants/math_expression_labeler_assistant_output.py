from pydantic import AliasChoices, Field

from math_rag.application.base.assistants import BaseAssistantOutput


class MathExpressionLabelerAssistantOutput(BaseAssistantOutput):
    label: str = Field(
        ...,
        validation_alias=AliasChoices('label', 'class'),
        serialization_alias='label',
    )
