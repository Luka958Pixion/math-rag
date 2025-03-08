from pymongo import AsyncMongoClient

from math_rag.infrastructure.models.documents import (
    MathExpressionClassificationDocument,
)

from .common_seeder import CommonSeeder


class MathExpressionClassificationSeeder(
    CommonSeeder[MathExpressionClassificationDocument]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
