from pathlib import Path

from arxiv import Client as _ArxivClient
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    Container,
    Dict,
    Factory,
    List,
    Provider,
    Singleton,
)
from huggingface_hub import HfApi
from label_studio_sdk.client import AsyncLabelStudio
from minio import Minio
from mpxpy.mathpix_client import MathpixClient as _MathpixClient
from openai import AsyncOpenAI
from pymongo import AsyncMongoClient
from qdrant_client import AsyncQdrantClient

from math_rag.application.base.indexers.documents import BaseDocumentIndexer
from math_rag.application.base.seeders.documents import BaseDocumentSeeder
from math_rag.application.base.seeders.embeddings import BaseEmbeddingSeeder
from math_rag.application.base.seeders.objects import BaseObjectSeeder
from math_rag.application.containers import ApplicationContainer
from math_rag.application.enums.inference import (
    EMInferenceProvider,
    LLMInferenceProvider,
    MMInferenceProvider,
)
from math_rag.infrastructure.base import BaseInitializer
from math_rag.infrastructure.clients import (
    ApptainerClient,
    ArxivClient,
    FileSystemClient,
    HPCClient,
    KatexClient,
    MathpixClient,
    PBSProClient,
    PrometheusAdminClient,
    PushgatewayClient,
    SFTPClient,
    SSHClient,
)
from math_rag.infrastructure.fine_tune.huggingface import FineTuneJobRunnerService
from math_rag.infrastructure.indexers.documents import (
    FineTuneJobIndexer,
    IndexIndexer,
    MathExpressionDatasetIndexer,
    MathExpressionDatasetTestIndexer,
    MathExpressionDatasetTestResultIndexer,
    MathExpressionDescriptionIndexer,
    MathExpressionGroupIndexer,
    MathExpressionIndexer,
    MathExpressionLabelIndexer,
    MathExpressionSampleIndexer,
    MathProblemIndexer,
    ObjectMetadataIndexer,
    TaskIndexer,
)
from math_rag.infrastructure.inference.huggingface import (
    TEIBatchEM,
    TEIBatchManagedEM,
    TGIBatchLLM,
    TGIBatchManagedLLM,
)
from math_rag.infrastructure.inference.openai import (
    OpenAIBatchEMRequestManagedScheduler,
    OpenAIBatchEMRequestScheduler,
    OpenAIBatchLLMRequestManagedScheduler,
    OpenAIBatchLLMRequestScheduler,
    OpenAIEM,
    OpenAILLM,
    OpenAIManagedEM,
    OpenAIManagedLLM,
    OpenAIManagedMM,
    OpenAIMM,
)
from math_rag.infrastructure.inference.routers import (
    ManagedEMRouter,
    ManagedLLMRouter,
    ManagedMMRouter,
)
from math_rag.infrastructure.migrations.documents import MathExpressionMigration
from math_rag.infrastructure.repositories.documents import (
    EMFailedRequestRepository,
    FineTuneJobRepository,
    IndexRepository,
    LLMFailedRequestRepository,
    MathExpressionDatasetRepository,
    MathExpressionDatasetTestRepository,
    MathExpressionDatasetTestResultRepository,
    MathExpressionDescriptionRepository,
    MathExpressionGroupRepository,
    MathExpressionLabelRepository,
    MathExpressionRepository,
    MathExpressionSampleRepository,
    MathProblemRepository,
    MMFailedRequestRepository,
    ObjectMetadataRepository,
    TaskRepository,
)
from math_rag.infrastructure.repositories.embeddings import (
    MathExpressionDescriptionOptimizedRepository,
)
from math_rag.infrastructure.repositories.files import GoogleDriveRepository
from math_rag.infrastructure.repositories.objects import MathArticleRepository
from math_rag.infrastructure.seeders.documents import (
    EMFailedRequestSeeder,
    FineTuneJobSeeder,
    IndexSeeder,
    LLMFailedRequestSeeder,
    MathExpressionDatasetSeeder,
    MathExpressionDatasetTestResultSeeder,
    MathExpressionDatasetTestSeeder,
    MathExpressionDescriptionSeeder,
    MathExpressionGroupSeeder,
    MathExpressionLabelSeeder,
    MathExpressionSampleSeeder,
    MathExpressionSeeder,
    MathProblemSeeder,
    MMFailedRequestSeeder,
    ObjectMetadataSeeder,
    TaskSeeder,
)
from math_rag.infrastructure.seeders.embeddings import MathExpressionDescriptionOptimizedSeeder
from math_rag.infrastructure.seeders.objects import MathArticleSeeder
from math_rag.infrastructure.services import (
    DatasetLoaderService,
    DatasetPublisherService,
    GPUStatsPusherService,
    HDBSCANClustererService,
    LabelStudioConfigBuilderService,
    LabelStudioTaskExporterService,
    LabelStudioTaskImporterService,
    LatexNodeWalkerService,
    LatexParserService,
    MathArticleParserService,
    PBSProResoucesUsedPusherService,
    PBSProResourceListLoaderService,
    PrometheusSnapshotLoaderService,
)


class InfrastructureContainer(DeclarativeContainer):
    config = Configuration()

    # Mongo
    config.mongo.host.from_env('MONGO_HOST')
    config.mongo.deployment.from_env('MONGO_DEPLOYMENT')

    async_mongo_client = Singleton(
        AsyncMongoClient,
        host=config.mongo.host,
        uuidRepresentation='standard',
    )

    mongo_kwargs = {
        'client': async_mongo_client,
        'deployment': config.mongo.deployment,
    }

    em_failed_request_repository = Factory(EMFailedRequestRepository, **mongo_kwargs)
    fine_tune_job_repository = Factory(FineTuneJobRepository, **mongo_kwargs)
    index_repository = Factory(IndexRepository, **mongo_kwargs)
    llm_failed_request_repository = Factory(LLMFailedRequestRepository, **mongo_kwargs)
    math_expression_dataset_repository = Factory(MathExpressionDatasetRepository, **mongo_kwargs)
    math_expression_dataset_test_repository = Factory(
        MathExpressionDatasetTestRepository, **mongo_kwargs
    )
    math_expression_dataset_test_result_repository = Factory(
        MathExpressionDatasetTestResultRepository, **mongo_kwargs
    )
    math_expression_description_repository = Factory(
        MathExpressionDescriptionRepository, **mongo_kwargs
    )
    math_expression_repository = Factory(MathExpressionRepository, **mongo_kwargs)
    math_expression_group_repository = Factory(MathExpressionGroupRepository, **mongo_kwargs)
    math_expression_label_repository = Factory(MathExpressionLabelRepository, **mongo_kwargs)
    math_expression_sample_repository = Factory(MathExpressionSampleRepository, **mongo_kwargs)
    math_problem_repository = Factory(MathProblemRepository, **mongo_kwargs)
    mm_failed_request_repository = Factory(MMFailedRequestRepository, **mongo_kwargs)
    object_metadata_repository = Factory(ObjectMetadataRepository, **mongo_kwargs)
    task_repository = Factory(TaskRepository, **mongo_kwargs)

    em_failed_request_seeder = Factory(EMFailedRequestSeeder, **mongo_kwargs)
    fine_tune_job_seeder = Factory(FineTuneJobSeeder, **mongo_kwargs)
    index_seeder = Factory(IndexSeeder, **mongo_kwargs)
    llm_failed_request_seeder = Factory(LLMFailedRequestSeeder, **mongo_kwargs)
    math_expression_dataset_seeder = Factory(MathExpressionDatasetSeeder, **mongo_kwargs)
    math_expression_dataset_test_seeder = Factory(MathExpressionDatasetTestSeeder, **mongo_kwargs)
    math_expression_description_seeder = Factory(MathExpressionDescriptionSeeder, **mongo_kwargs)
    math_expression_dataset_test_result_seeder = Factory(
        MathExpressionDatasetTestResultSeeder, **mongo_kwargs
    )
    math_expression_group_seeder = Factory(MathExpressionGroupSeeder, **mongo_kwargs)
    math_expression_label_seeder = Factory(MathExpressionLabelSeeder, **mongo_kwargs)
    math_expression_seeder = Factory(MathExpressionSeeder, **mongo_kwargs)
    math_expression_sample_seeder = Factory(MathExpressionSampleSeeder, **mongo_kwargs)
    math_problem_seeder = Factory(MathProblemSeeder, **mongo_kwargs)
    mm_failed_request_seeder = Factory(MMFailedRequestSeeder, **mongo_kwargs)
    object_metadata_seeder = Factory(ObjectMetadataSeeder, **mongo_kwargs)
    task_seeder = Factory(TaskSeeder, **mongo_kwargs)

    document_seeders: Provider[list[BaseDocumentSeeder]] = List(
        em_failed_request_seeder,
        fine_tune_job_seeder,
        index_seeder,
        llm_failed_request_seeder,
        math_expression_dataset_seeder,
        math_expression_dataset_test_seeder,
        math_expression_description_seeder,
        math_expression_dataset_test_result_seeder,
        math_expression_group_seeder,
        math_expression_label_seeder,
        math_expression_seeder,
        math_expression_sample_seeder,
        math_problem_seeder,
        mm_failed_request_seeder,
        object_metadata_seeder,
        task_seeder,
    )

    fine_tune_job_indexer = Factory(FineTuneJobIndexer, **mongo_kwargs)
    index_indexer = Factory(IndexIndexer, **mongo_kwargs)
    math_expression_dataset_indexer = Factory(MathExpressionDatasetIndexer, **mongo_kwargs)
    math_expression_dataset_test_indexer = Factory(MathExpressionDatasetTestIndexer, **mongo_kwargs)
    math_expression_dataset_test_result_indexer = Factory(
        MathExpressionDatasetTestResultIndexer, **mongo_kwargs
    )
    math_expression_description_indexer = Factory(MathExpressionDescriptionIndexer, **mongo_kwargs)
    math_expression_group_indexer = Factory(MathExpressionGroupIndexer, **mongo_kwargs)
    math_expression_label_indexer = Factory(MathExpressionLabelIndexer, **mongo_kwargs)
    math_expression_indexer = Factory(MathExpressionIndexer, **mongo_kwargs)
    math_expression_sample_indexer = Factory(MathExpressionSampleIndexer, **mongo_kwargs)
    math_problem_indexer = Factory(MathProblemIndexer, **mongo_kwargs)
    object_metadata_indexer = Factory(ObjectMetadataIndexer, **mongo_kwargs)
    task_indexer = Factory(TaskIndexer, **mongo_kwargs)

    document_indexers: Provider[list[BaseDocumentIndexer]] = List(
        fine_tune_job_indexer,
        index_indexer,
        math_expression_dataset_indexer,
        math_expression_dataset_test_indexer,
        math_expression_dataset_test_result_indexer,
        math_expression_description_indexer,
        math_expression_group_indexer,
        math_expression_label_indexer,
        math_expression_indexer,
        math_expression_sample_indexer,
        math_problem_indexer,
        object_metadata_indexer,
        task_indexer,
    )

    math_expression_migration = Factory(MathExpressionMigration, **mongo_kwargs)

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
        object_metadata_repository=object_metadata_repository,
    )

    # Neo4j

    # Qdrant
    config.qdrant.url.from_env('QDRANT_URL')

    async_qdrant_client = Singleton(
        AsyncQdrantClient,
        url=config.qdrant.url,
    )

    math_expression_description_optimized_seeder = Factory(
        MathExpressionDescriptionOptimizedSeeder,
        client=async_qdrant_client,
    )

    embedding_seeders: Provider[list[BaseEmbeddingSeeder]] = List(
        math_expression_description_optimized_seeder
    )

    math_expression_description_optimized_repository = Factory(
        MathExpressionDescriptionOptimizedRepository,
        client=async_qdrant_client,
    )

    # Google
    resource = Singleton(
        GoogleDriveRepository.get_resource,
        credentials_path=Path('../secrets/google/credentials.json'),
        token_path=Path('../secrets/google/token.json'),
    )

    google_drive_repository = Factory(GoogleDriveRepository, resource=resource)

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
    openai_mm = Factory(OpenAIMM, client=async_openai_client)

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
    openai_managed_mm = Factory(
        OpenAIManagedMM,
        mm=openai_mm,
        mm_settings_loader_service=ApplicationContainer.mm_settings_loader_service,
        mm_failed_request_repository=mm_failed_request_repository,
    )

    openai_batch_em_request_scheduler = Factory(
        OpenAIBatchEMRequestScheduler,
        em=openai_managed_em,
    )
    openai_batch_llm_request_scheduler = Factory(
        OpenAIBatchLLMRequestScheduler,
        llm=openai_managed_llm,
    )

    openai_batch_em_request_managed_scheduler = Factory(
        OpenAIBatchEMRequestManagedScheduler,
        scheduler=openai_batch_em_request_scheduler,
        em_settings_loader_service=ApplicationContainer.em_settings_loader_service,
    )
    openai_batch_llm_request_managed_scheduler = Factory(
        OpenAIBatchLLMRequestManagedScheduler,
        scheduler=openai_batch_llm_request_scheduler,
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
    latex_node_walker_service = Factory(LatexNodeWalkerService)
    math_article_parser_service = Factory(
        MathArticleParserService,
        latex_parser_service=latex_parser_service,
        latex_node_walker_service=latex_node_walker_service,
    )

    # KaTeX
    config.katex.base_url.from_env('KATEX_BASE_URL')

    katex_client = Factory(
        KatexClient,
        base_url=config.katex.base_url,
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

    # Pushgateway
    config.pushgateway.base_url.from_env('PUSHGATEWAY_BASE_URL')

    pushgateway_client = Factory(PushgatewayClient, base_url=config.pushgateway.base_url)

    # Prometheus Admin
    config.prometheus.hpc.base_url.from_env('PROMETHEUS_HPC_BASE_URL')

    prometheus_hpc_admin_client = Factory(
        PrometheusAdminClient, base_url=config.prometheus.hpc.base_url
    )

    # Apptainer
    config.apptainer.base_url.from_env('APPTAINER_BASE_URL')

    apptainer_client = Factory(
        ApptainerClient,
        base_url=config.apptainer.base_url,
    )

    pbs_pro_resource_list_loader_service = Factory(PBSProResourceListLoaderService)

    # TEI
    tei_batch_em = Factory(
        TEIBatchEM,
        file_system_client=file_system_client,
        pbs_pro_client=pbs_pro_client,
        sftp_client=sftp_client,
        apptainer_client=apptainer_client,
        pbs_pro_resource_list_loader_service=pbs_pro_resource_list_loader_service,
    )
    tei_batch_managed_em = Factory(
        TEIBatchManagedEM,
        em=tei_batch_em,
        em_settings_loader_service=ApplicationContainer.em_settings_loader_service,
    )

    # TGI
    tgi_batch_llm = Factory(
        TGIBatchLLM,
        file_system_client=file_system_client,
        pbs_pro_client=pbs_pro_client,
        sftp_client=sftp_client,
        apptainer_client=apptainer_client,
        pbs_pro_resource_list_loader_service=pbs_pro_resource_list_loader_service,
    )
    tgi_batch_managed_llm = Factory(
        TGIBatchManagedLLM,
        llm=tgi_batch_llm,
        llm_settings_loader_service=ApplicationContainer.llm_settings_loader_service,
    )

    # LoRA
    fine_tune_job_runner_service = Factory(
        FineTuneJobRunnerService,
        file_system_client=file_system_client,
        pbs_pro_client=pbs_pro_client,
        sftp_client=sftp_client,
        apptainer_client=apptainer_client,
        pbs_pro_resource_list_loader_service=pbs_pro_resource_list_loader_service,
    )

    initializers: Provider[list[BaseInitializer]] = List(
        tei_batch_em, tgi_batch_llm, fine_tune_job_runner_service
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

    hugging_face_api = Singleton(
        HfApi,
        endpoint=config.hugging_face.base_url,
        token=config.hugging_face.token,
    )

    dataset_loader_service = Factory(
        DatasetLoaderService,
        hugging_face_api=hugging_face_api,
        hugging_face_username=config.hugging_face.username,
        hugging_face_token=config.hugging_face.token,
    )
    dataset_publisher_service = Factory(
        DatasetPublisherService,
        hugging_face_api=hugging_face_api,
        hugging_face_username=config.hugging_face.username,
        hugging_face_token=config.hugging_face.token,
    )

    # Label Studio
    config.label_studio.base_url.from_env('LABEL_STUDIO_BASE_URL')
    config.label_studio.api_key.from_env('LABEL_STUDIO_API_KEY')

    async_label_studio = Singleton(
        AsyncLabelStudio,
        base_url=config.label_studio.base_url,
        api_key=config.label_studio.api_key,
    )

    label_studio_config_builder_service = Factory(LabelStudioConfigBuilderService)
    label_studio_task_exporter_service = Factory(
        LabelStudioTaskExporterService,
        async_label_studio=async_label_studio,
    )
    label_studio_task_importer_service = Factory(
        LabelStudioTaskImporterService,
        async_label_studio=async_label_studio,
    )

    # Pushgateway
    gpu_stats_pusher_service = Factory(
        GPUStatsPusherService,
        hpc_client=hpc_client,
        pushgateway_base_url=config.pushgateway.base_url,
    )
    pbs_pro_resources_used_pusher_service = Factory(
        PBSProResoucesUsedPusherService,
        pbs_pro_client=pbs_pro_client,
        pushgateway_base_url=config.pushgateway.base_url,
    )

    # clustering
    hdbscan_clusterer_service = Factory(HDBSCANClustererService)

    # routers
    inference_provider_to_managed_em = Dict(
        {
            EMInferenceProvider.OPEN_AI: openai_managed_em,
            EMInferenceProvider.HUGGING_FACE: tei_batch_managed_em,
        }
    )
    inference_provider_to_managed_llm = Dict(
        {
            LLMInferenceProvider.OPEN_AI: openai_managed_llm,
            LLMInferenceProvider.HUGGING_FACE: tgi_batch_managed_llm,
        }
    )
    inference_provider_to_managed_mm = Dict(
        {
            MMInferenceProvider.OPEN_AI: openai_managed_llm,
        }
    )

    managed_em_router = Factory(
        ManagedEMRouter,
        inference_provider_to_managed_em=inference_provider_to_managed_em,
    )
    managed_llm_router = Factory(
        ManagedLLMRouter,
        inference_provider_to_managed_llm=inference_provider_to_managed_llm,
    )
    managed_mm_router = Factory(
        ManagedMMRouter,
        inference_provider_to_managed_llm=inference_provider_to_managed_mm,
    )

    # ApplicationContainer
    application_container = Container(
        ApplicationContainer,
        arxiv_client=arxiv_client,
        katex_client=katex_client,
        latex_converter_client=mathpix_client,
        managed_em=managed_em_router,
        managed_llm=managed_llm_router,
        managed_mm=managed_mm_router,
        managed_em_scheduler=openai_batch_em_request_managed_scheduler,
        managed_llm_scheduler=openai_batch_llm_request_managed_scheduler,
        clusterer_service=hdbscan_clusterer_service,
        dataset_loader_service=dataset_loader_service,
        dataset_publisher_service=dataset_publisher_service,
        gpu_stats_pusher_service=gpu_stats_pusher_service,
        math_article_parser_service=math_article_parser_service,
        label_config_builder_service=label_studio_config_builder_service,
        label_task_exporter_service=label_studio_task_exporter_service,
        label_task_importer_service=label_studio_task_importer_service,
        fine_tune_job_runner_service=fine_tune_job_runner_service,
        prometheus_snapshot_loader_service=prometheus_snapshot_loader_service,
        pbs_pro_resources_used_pusher_service=pbs_pro_resources_used_pusher_service,
        fine_tune_job_repository=fine_tune_job_repository,
        index_repository=index_repository,
        math_expression_dataset_repository=math_expression_dataset_repository,
        math_expression_dataset_test_repository=math_expression_dataset_test_repository,
        math_expression_dataset_test_result_repository=math_expression_dataset_test_result_repository,
        math_expression_sample_repository=math_expression_sample_repository,
        math_article_repository=math_article_repository,
        math_expression_repository=math_expression_repository,
        math_expression_label_repository=math_expression_label_repository,
        math_problem_repository=math_problem_repository,
        task_repository=task_repository,
    )
