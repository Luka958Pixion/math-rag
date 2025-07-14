from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseMathProblemSolutionRepository
from math_rag.core.models import MathProblemSolution
from math_rag.infrastructure.mappings.documents import MathProblemSolutionMapping
from math_rag.infrastructure.models.documents import MathProblemSolutionDocument

from .document_repository import DocumentRepository


class MathProblemSolutionRepository(
    BaseMathProblemSolutionRepository,
    DocumentRepository[
        MathProblemSolution, MathProblemSolutionDocument, MathProblemSolutionMapping
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
