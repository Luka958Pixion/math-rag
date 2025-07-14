from pydantic import BaseModel

from math_rag.core.models import MathProblemSolution


class Response(BaseModel):
    math_problem_solution: MathProblemSolution
