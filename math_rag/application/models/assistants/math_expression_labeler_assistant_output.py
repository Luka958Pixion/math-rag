from pydantic import AliasChoices, Field

from math_rag.application.base.assistants import BaseAssistantOutput
from math_rag.core.enums import MathExpressionLabelEnum


class MathExpressionLabelerAssistantOutput(BaseAssistantOutput):
    label: MathExpressionLabelEnum = Field(
        ...,
        validation_alias=AliasChoices('label', 'class'),
        serialization_alias='label',
    )
