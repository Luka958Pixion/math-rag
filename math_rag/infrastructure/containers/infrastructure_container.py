from pathlib import Path

from arxiv import Client as _ArxivClient
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Callable,
    Configuration,
    Container,
    Factory,
    List,
    Provider,
    Singleton,
)
from minio import Minio
from mpxpy.mathpix_client import MathpixClient as _MathpixClient
from openai import AsyncOpenAI
from pymongo import AsyncMongoClient

from math_rag.application.base.indexers.documents import BaseDocumentIndexer
from math_rag.application.base.seeders.documents import BaseDocumentSeeder
from math_rag.application.base.seeders.objects import BaseObjectSeeder
from math_rag.application.containers import ApplicationContainer
from math_rag.infrastructure.clients import (
    ApptainerClient,
    ArxivClient,
    FileSystemClient,
    HPCClient,
    KatexClient,
    MathpixClient,
    PBSProClient,
    SFTPClient,
    SSHClient,
)
from math_rag.infrastructure.indexers.documents import (
    IndexIndexer,
    MathExpressionDatasetIndexer,
    MathExpressionIndexer,
    MathExpressionLabelIndexer,
    MathExpressionSampleIndexer,
)
from math_rag.infrastructure.inference.huggingface import TEIBatchEM, TGIBatchLLM
from math_rag.infrastructure.inference.openai import (
    OpenAIBatchLLMRequestManagedScheduler,
    OpenAIBatchLLMRequestScheduler,
    OpenAIEM,
    OpenAILLM,
    OpenAIManagedEM,
    OpenAIManagedLLM,
)
from math_rag.infrastructure.repositories.documents import (
    EMFailedRequestRepository,
    IndexRepository,
    LLMFailedRequestRepository,
    MathExpressionDatasetRepository,
    MathExpressionLabelRepository,
    MathExpressionRepository,
    MathExpressionSampleRepository,
)
from math_rag.infrastructure.repositories.files import GoogleFileRepository
from math_rag.infrastructure.repositories.objects import MathArticleRepository
from math_rag.infrastructure.seeders.documents import (
    EMFailedRequestSeeder,
    IndexSeeder,
    LLMFailedRequestSeeder,
    MathExpressionDatasetSeeder,
    MathExpressionLabelSeeder,
    MathExpressionSampleSeeder,
    MathExpressionSeeder,
)
from math_rag.infrastructure.seeders.objects import MathArticleSeeder
from math_rag.infrastructure.services import (
    DatasetPublisherService,
    LatexParserService,
    LatexVisitorService,
    PrometheusSnapshotLoaderService,
    TEISettingsLoaderService,
    TGISettingsLoaderService,
)


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

    object_seeders: Provider[list[BaseObjectSeeder]] = List(math_article_seeder)

    math_article_repository = Factory(
        MathArticleRepository,
        client=minio_client,
    )

    # Mongo
    config.mongo.host.from_env('MONGO_HOST')
    config.mongo.deployment.from_env('MONGO_DEPLOYMENT')

    mongo_client = Singleton(
        AsyncMongoClient,
        host=config.mongo.host,
        uuidRepresentation='standard',
    )

    mongo_kwargs = {
        'client': mongo_client,
        'deployment': config.mongo.deployment,
    }

    em_failed_request_repository = Factory(EMFailedRequestRepository, **mongo_kwargs)
    index_repository = Factory(IndexRepository, **mongo_kwargs)
    llm_failed_request_repository = Factory(LLMFailedRequestRepository, **mongo_kwargs)
    math_expression_dataset_repository = Factory(MathExpressionDatasetRepository, **mongo_kwargs)
    math_expression_repository = Factory(MathExpressionRepository, **mongo_kwargs)
    math_expression_label_repository = Factory(MathExpressionLabelRepository, **mongo_kwargs)
    math_expression_sample_repository = Factory(MathExpressionSampleRepository, **mongo_kwargs)

    em_failed_request_seeder = Factory(EMFailedRequestSeeder, **mongo_kwargs)
    index_seeder = Factory(IndexSeeder, **mongo_kwargs)
    llm_failed_request_seeder = Factory(LLMFailedRequestSeeder, **mongo_kwargs)
    math_expression_dataset_seeder = Factory(MathExpressionDatasetSeeder, **mongo_kwargs)
    math_expression_label_seeder = Factory(MathExpressionLabelSeeder, **mongo_kwargs)
    math_expression_seeder = Factory(MathExpressionSeeder, **mongo_kwargs)
    math_expression_sample_seeder = Factory(MathExpressionSampleSeeder, **mongo_kwargs)

    document_seeders: Provider[list[BaseDocumentSeeder]] = List(
        em_failed_request_seeder,
        index_seeder,
        llm_failed_request_seeder,
        math_expression_dataset_seeder,
        math_expression_label_seeder,
        math_expression_seeder,
        math_expression_sample_seeder,
    )

    index_indexer = Factory(IndexIndexer, **mongo_kwargs)
    math_expression_dataset_indexer = Factory(MathExpressionDatasetIndexer, **mongo_kwargs)
    math_expression_label_indexer = Factory(MathExpressionLabelIndexer, **mongo_kwargs)
    math_expression_indexer = Factory(MathExpressionIndexer, **mongo_kwargs)
    math_expression_sample_indexer = Factory(MathExpressionSampleIndexer, **mongo_kwargs)

    document_indexers: Provider[list[BaseDocumentIndexer]] = List(
        index_indexer,
        math_expression_dataset_indexer,
        math_expression_label_indexer,
        math_expression_indexer,
        math_expression_sample_indexer,
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

    openai_em = Factory(OpenAIEM, client=async_openai_client)
    openai_llm = Factory(OpenAILLM, client=async_openai_client)

    openai_managed_em = Factory(
        OpenAIManagedEM,
        em=openai_em,
        em_settings_loader_service=ApplicationContainer.em_settings_loader_service,
        em_failed_request_repository=em_failed_request_repository,
    )
    openai_managed_llm = Factory(
        OpenAIManagedLLM,
        llm=openai_llm,
        llm_settings_loader_service=ApplicationContainer.llm_settings_loader_service,
        llm_failed_request_repository=llm_failed_request_repository,
    )

    openai_scheduler = Factory(
        OpenAIBatchLLMRequestScheduler,
        llm=openai_managed_llm,
    )
    openai_managed_scheduler = Factory(
        OpenAIBatchLLMRequestManagedScheduler,
        scheduler=openai_scheduler,
        llm_settings_loader_service=ApplicationContainer.llm_settings_loader_service,
    )

    # arXiv
    _arxiv_client = Singleton(_ArxivClient)
    arxiv_client = Factory(ArxivClient, client=_arxiv_client)

    # Mathpix
    config.mathpix.app_id.from_env('MATHPIX_APP_ID')
    config.mathpix.app_key.from_env('MATHPIX_APP_KEY')
    config.mathpix.api_url.from_env('MATHPIX_URL')

    _mathpix_client = Singleton(
        _MathpixClient,
        app_id=config.mathpix.app_id,
        app_key=config.mathpix.app_key,
        api_url=config.mathpix.api_url,
    )

    mathpix_client = Factory(MathpixClient, client=_mathpix_client)

    # LaTeX
    latex_parser_service = Factory(LatexParserService)
    latex_visitor_service = Factory(LatexVisitorService)

    # KaTeX
    config.katex.port.from_env('KATEX_PORT')
    katex_client = Factory(
        KatexClient,
        base_url=Callable(lambda port: f'http://host.docker.internal:{port}', config.katex.port),
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
        tei_settings_loader_service=tei_settings_loader_service,
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

    # Prometheus
    prometheus_snapshot_loader_service = Factory(
        PrometheusSnapshotLoaderService,
        file_system_client=file_system_client,
        pbs_pro_client=pbs_pro_client,
        sftp_client=sftp_client,
    )

    # HuggingFace
    config.hugging_face.base_url.from_env('HF_BASE_URL')
    config.hugging_face.username.from_env('HF_USERNAME')
    config.hugging_face.token.from_env('HF_TOKEN')

    dataset_publisher_service = Factory(
        DatasetPublisherService,
        hugging_face_base_url=config.hugging_face.base_url,
        hugging_face_username=config.hugging_face.username,
        hugging_face_token=config.hugging_face.token,
    )

    # ApplicationContainer
    application_container = Container(
        ApplicationContainer,
        arxiv_client=arxiv_client,
        katex_client=katex_client,
        managed_llm=openai_managed_llm,
        managed_scheduler=openai_managed_scheduler,
        latex_parser_service=latex_parser_service,
        latex_visitor_service=latex_visitor_service,
        dataset_publisher_service=dataset_publisher_service,
        index_repository=index_repository,
        math_expression_dataset_repository=math_expression_dataset_repository,
        math_expression_sample_repository=math_expression_sample_repository,
        math_article_repository=math_article_repository,
        math_expression_repository=math_expression_repository,
        math_expression_label_repository=math_expression_label_repository,
    )
