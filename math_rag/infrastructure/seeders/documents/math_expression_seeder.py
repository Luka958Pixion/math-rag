from pymongo import AsyncMongoClient

from math_rag.core.models import MathExpression

from .common_seeder import CommonSeeder


class MathExpressionSeeder(CommonSeeder[MathExpression]):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
