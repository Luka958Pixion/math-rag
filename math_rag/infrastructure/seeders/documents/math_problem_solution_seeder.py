from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import MathProblemSolutionDocument

from .document_seeder import DocumentSeeder


class MathProblemSolutionSeeder(DocumentSeeder[MathProblemSolutionDocument]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
