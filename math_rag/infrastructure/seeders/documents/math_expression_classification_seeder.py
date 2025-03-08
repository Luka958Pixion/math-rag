from pymongo import AsyncMongoClient

from math_rag.core.models import MathExpressionClassification

from .common_seeder import CommonSeeder


class MathExpressionClassificationSeeder(CommonSeeder[MathExpressionClassification]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
