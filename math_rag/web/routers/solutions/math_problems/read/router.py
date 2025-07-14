from logging import getLogger
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from math_rag.application.base.repositories.documents import BaseMathProblemSolutionRepository
from math_rag.application.containers import ApplicationContainer

from .response import Response


logger = getLogger(__name__)
router = APIRouter()


@router.get('/solutions/math-problems', response_model=Response)
@inject
async def read_math_problem_solution(
    math_problem_id: UUID = Query(...),
    math_problem_solution_repository: BaseMathProblemSolutionRepository = Depends(
        Provide[ApplicationContainer.math_problem_solution_repository]
    ),
):
    math_problem_solution = await math_problem_solution_repository.find_one(
        filter=dict(math_problem_id=math_problem_id)
    )

    if math_problem_solution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return Response(math_problem_solution=math_problem_solution)
