from pathlib import Path

from arxiv import Client
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Singleton
from minio import Minio
from openai import AsyncOpenAI
from pymongo import AsyncMongoClient

from math_rag.application.assistants import (
    KCAssistant,
    MECAssistant,
)
from math_rag.infrastructure.inference import OpenAILLM
from math_rag.infrastructure.repositories.documents import (
    MathExpressionClassificationRepository,
    MathExpressionRepository,
)
from math_rag.infrastructure.repositories.files import GoogleFileRepository
from math_rag.infrastructure.repositories.objects import MathArticleRepository
from math_rag.infrastructure.seeders.documents import (
    MathExpressionClassificationSeeder,
    MathExpressionSeeder,
)
from math_rag.infrastructure.seeders.objects import MathArticleSeeder
from math_rag.infrastructure.services import (
    ArxivSearcherService,
    KatexValidatorService,
    LatexParserService,
    LatexVisitorService,
)


class InfrastructureContainer(DeclarativeContainer):
    config = Configuration()

    # --------------
    # Infrastructure
    # --------------

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

    math_expression_classification_seeder = Factory(
        MathExpressionClassificationSeeder,
        client=mongo_client,
        deployment=config.mongo.deployment,
    )
    math_expression_classification_repository = Factory(
        MathExpressionClassificationRepository,
        client=mongo_client,
        deployment=config.mongo.deployment,
    )

    # Neo4j

    # Qdrant

    # Google
    resource = Singleton(
        GoogleFileRepository.get_resource,
        credentials_path=Path('../secrets/google/credentials.json'),
        token_path=Path('../secrets/google/token.json'),
    )

    google_file_repository = Factory(GoogleFileRepository, resource=resource)

    # OpenAI
    config.openai.base_url.from_env('OPENAI_BASE_URL')
    config.openai.api_key.from_env('OPENAI_API_KEY')

    async_openai_client = Singleton(
        AsyncOpenAI,
        base_url=config.openai.base_url,
        api_key=config.openai.api_key,
    )

    openai_llm = Factory(OpenAILLM, client=async_openai_client)

    # arXiv
    arxiv_client = Singleton(Client)
    arxiv_searcher_service = Factory(ArxivSearcherService, client=arxiv_client)

    # LaTeX
    latex_parser_service = Factory(LatexParserService)
    latex_visitor_service = Factory(LatexVisitorService)

    # KaTeX
    katex_validator_service = Factory(KatexValidatorService)

    # -----------
    # Application
    # -----------

    # KaTeX
    katex_correction_assistant = Factory(
        KCAssistant,
        llm=openai_llm,
    )
    math_expression_classification_assistant = Factory(MECAssistant, llm=openai_llm)
