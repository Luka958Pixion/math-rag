from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Singleton
from minio import Minio

from math_rag.infrastructure.repositories.objects import MathArticleRepository


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

    math_article_repository = Factory(
        MathArticleRepository,
        client=minio_client,
    )

    # Mongo

    # Neo4j

    # Qdrant
