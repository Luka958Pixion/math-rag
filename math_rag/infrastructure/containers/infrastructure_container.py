from pathlib import Path

from arxiv import Client
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Callable,
    Configuration,
    Container,
    Factory,
    Singleton,
)
from minio import Minio
from openai import AsyncOpenAI
from pymongo import AsyncMongoClient

from math_rag.application.assistants import (
    KCAssistant,
    MECAssistant,
)
from math_rag.application.containers import ApplicationContainer
from math_rag.infrastructure.clients import (
    ApptainerClient,
    ArxivClient,
    FileSystemClient,
    HPCClient,
    KatexClient,
    PBSProClient,
    SFTPClient,
    SSHClient,
)
from math_rag.infrastructure.inference.huggingface import TEIBatchEM, TGIBatchLLM
from math_rag.infrastructure.inference.openai import (
    OpenAIEM,
    OpenAILLM,
    OpenAIManagedEM,
    OpenAIManagedLLM,
)
from math_rag.infrastructure.repositories.documents import (
    EMFailedRequestRepository,
    LLMFailedRequestRepository,
    MathExpressionClassificationRepository,
    MathExpressionRepository,
)
from math_rag.infrastructure.repositories.files import GoogleFileRepository
from math_rag.infrastructure.repositories.objects import MathArticleRepository
from math_rag.infrastructure.seeders.documents import (
    EMFailedRequestSeeder,
    LLMFailedRequestSeeder,
    MathExpressionClassificationSeeder,
    MathExpressionSeeder,
)
from math_rag.infrastructure.seeders.objects import MathArticleSeeder
from math_rag.infrastructure.services import (
    LatexParserService,
    LatexVisitorService,
    TEISettingsLoaderService,
    TGISettingsLoaderService,
)


class InfrastructureContainer(DeclarativeContainer):
    config = Configuration()
    application_container = Container(ApplicationContainer).container

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

    mongo_kwargs = {
        'client': mongo_client,
        'deployment': config.mongo.deployment,
    }

    math_expression_seeder = Factory(MathExpressionSeeder, **mongo_kwargs)
    math_expression_repository = Factory(MathExpressionRepository, **mongo_kwargs)
    em_failed_request_repository = Factory(EMFailedRequestRepository, **mongo_kwargs)
    llm_failed_request_repository = Factory(LLMFailedRequestRepository, **mongo_kwargs)

    math_expression_classification_seeder = Factory(
        MathExpressionClassificationSeeder, **mongo_kwargs
    )
    math_expression_classification_repository = Factory(
        MathExpressionClassificationRepository, **mongo_kwargs
    )
    em_failed_request_seeder = Factory(EMFailedRequestSeeder, **mongo_kwargs)
    llm_failed_request_seeder = Factory(LLMFailedRequestSeeder, **mongo_kwargs)

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

    openai_em = Factory(OpenAIEM, client=async_openai_client)
    openai_llm = Factory(OpenAILLM, client=async_openai_client)

    openai_managed_em = Factory(
        OpenAIManagedEM,
        em=openai_em,
        em_settings_loader_service=application_container.em_settings_loader_service,
        em_failed_request_repository=em_failed_request_repository,
    )
    openai_managed_llm = Factory(
        OpenAIManagedLLM,
        llm=openai_llm,
        llm_settings_loader_service=application_container.llm_settings_loader_service,
        llm_failed_request_repository=llm_failed_request_repository,
    )

    # arXiv
    _arxiv_client = Singleton(Client)
    arxiv_client = Factory(ArxivClient, client=_arxiv_client)

    # LaTeX
    latex_parser_service = Factory(LatexParserService)
    latex_visitor_service = Factory(LatexVisitorService)

    # KaTeX
    config.katex.port.from_env('KATEX_PORT')
    katex_client = Factory(
        KatexClient,
        base_url=Callable(
            lambda port: f'http://host.docker.internal:{port}', config.katex.port
        ),
    )

    ## SSH
    config.hpc.user.from_env('HPC_USER')
    config.hpc.host.from_env('HPC_HOST')
    config.hpc.passphrase.from_env('HPC_PASSPHRASE')

    ssh_client = Factory(
        SSHClient,
        user=config.hpc.user,
        host=config.hpc.host,
        passphrase=config.hpc.passphrase,
    )

    # file system
    file_system_client = Factory(FileSystemClient, ssh_client=ssh_client)

    # HPC
    hpc_client = Factory(HPCClient, ssh_client=ssh_client)

    ## SFTP
    sftp_client = Factory(SFTPClient, ssh_client=ssh_client)

    # PBS Pro
    pbs_pro_client = Factory(PBSProClient, ssh_client=ssh_client)

    # Apptainer
    config.apptainer.port.from_env('APPTAINER_PORT')

    apptainer_client = Factory(
        ApptainerClient,
        base_url=Callable(
            lambda port: f'http://host.docker.internal:{port}', config.apptainer.port
        ),
    )

    # TEI
    tei_settings_loader_service = Factory(TEISettingsLoaderService)

    tei_batch_em = Factory(
        TEIBatchEM,
        file_system_client=file_system_client,
        pbs_pro_client=pbs_pro_client,
        sftp_client=sftp_client,
        apptainer_client=apptainer_client,
        tgi_settings_loader_service=tei_settings_loader_service,
    )

    # TGI
    tgi_settings_loader_service = Factory(TGISettingsLoaderService)

    tgi_batch_llm = Factory(
        TGIBatchLLM,
        file_system_client=file_system_client,
        pbs_pro_client=pbs_pro_client,
        sftp_client=sftp_client,
        apptainer_client=apptainer_client,
        tgi_settings_loader_service=tgi_settings_loader_service,
    )

    # -----------
    # Application
    # -----------

    # KaTeX
    kc_assistant = Factory(KCAssistant, llm=openai_managed_llm)
    math_expression_classification_assistant = Factory(
        MECAssistant, llm=openai_managed_llm
    )
