from math_rag.infrastructure.base import BaseDocumentView


class MathExpressionSampleDocumentView(BaseDocumentView):
    latex: str
    label: str
