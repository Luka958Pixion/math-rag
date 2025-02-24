from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Singleton
from minio import Minio
from pymongo import AsyncMongoClient

from math_rag.infrastructure.repositories.documents import MathExpressionRepository
from math_rag.infrastructure.repositories.objects import MathArticleRepository
from math_rag.infrastructure.seeders.documents import MathExpressionSeeder
from math_rag.infrastructure.seeders.objects import MathArticleSeeder


class InfrastructureContainer(DeclarativeContainer):
    config = Configuration()

    # Minio
    config.minio.endpoint.from_env('MINIO_ENDPOINT')
    config.minio.access_key.from_env('MINIO_ACCESS_KEY')
    config.minio.secret_key.from_env('MINIO_SECRET_KEY')

    minio_client = Singleton(
        Minio,
        endpoint=config.minio.endpoint,
        access_key=config.minio.access_key,
        secret_key=config.minio.secret_key,
        secure=False,
    )

    math_article_seeder = Factory(MathArticleSeeder, client=minio_client)
    math_article_repository = Factory(
        MathArticleRepository,
        client=minio_client,
    )

    # Mongo
    config.mongo.host.from_env('MONGO_HOST')
    config.mongo.deployment.from_env('DEPLOYMENT')

    mongo_client = Singleton(
        AsyncMongoClient,
        host=config.mongo.host,
        uuidRepresentation='standard',
    )

    math_expression_seeder = Factory(
        MathExpressionSeeder,
        client=mongo_client,
        deployment=config.mongo.deployment,
    )
    math_expression_repository = Factory(
        MathExpressionRepository,
        client=mongo_client,
        deployment=config.mongo.deployment,
    )

    # Neo4j

    # Qdrant
