from pydantic import BaseModel

from math_rag.core.models import MathExpressionIndexBuildDetails


class Request(BaseModel):
    build_details: MathExpressionIndexBuildDetails
