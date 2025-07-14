from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    Dependency,
    Factory,
    List,
    Provider,
    Singleton,
)

from math_rag.application.assistants import (
    KatexCorrectorAssistant,
    KatexCorrectorRetrierAssistant,
    MathExpressionComparatorAssistant,
    MathExpressionDescriptionOptimizerAssistant,
    MathExpressionDescriptionWriterAssistant,
    MathExpressionLabelerAssistant,
    MathExpressionRelationshipDescriptionWriterAssistant,
    MathExpressionRelationshipDetectorAssistant,
)
from math_rag.application.base.clients import (
    BaseArxivClient,
    BaseKatexClient,
    BaseLatexConverterClient,
)
from math_rag.application.base.fine_tune import BaseFineTuneJobRunnerService
from math_rag.application.base.inference import (
    BaseBatchEMRequestManagedScheduler,
    BaseBatchLLMRequestManagedScheduler,
    BaseManagedEM,
    BaseManagedLLM,
    BaseManagedMM,
)
from math_rag.application.base.repositories.documents import (
    BaseFineTuneJobRepository,
    BaseMathArticleChunkRepository,
    BaseMathExpressionContextRepository,
    BaseMathExpressionDatasetRepository,
    BaseMathExpressionDatasetTestRepository,
    BaseMathExpressionDatasetTestResultRepository,
    BaseMathExpressionDescriptionOptRepository,
    BaseMathExpressionDescriptionRepository,
    BaseMathExpressionGroupRepository,
    BaseMathExpressionIndexRepository,
    BaseMathExpressionLabelRepository,
    BaseMathExpressionRelationshipDescriptionRepository,
    BaseMathExpressionRelationshipRepository,
    BaseMathExpressionRepository,
    BaseMathExpressionSampleRepository,
    BaseMathProblemRepository,
    BaseTaskRepository,
)
from math_rag.application.base.repositories.embeddings import (
    BaseMathExpressionDescriptionOptRepository as BaseMathExpressionDescriptionOptEmbeddingRepository,
)
from math_rag.application.base.repositories.graphs import (
    BaseMathExpressionGroupRepository as BaseMathExpressionGroupGraphRepository,
    BaseMathExpressionRepository as BaseMathExpressionGraphRepository,
)
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import (
    BaseDatasetLoaderService,
    BaseDatasetPublisherService,
    BaseGPUStatsPusherService,
    BaseGrouperService,
    BaseLabelConfigBuilderService,
    BaseLabelTaskExporterService,
    BaseLabelTaskImporterService,
    BaseMathArticleParserService,
    BasePBSProResoucesUsedPusherService,
    BasePrometheusSnapshotLoaderService,
)
from math_rag.application.base.services.backgrounds import BaseBackgroundService
from math_rag.application.embedders import DefaultEmbedder
from math_rag.application.moderators import DefaultModerator
from math_rag.application.services import (
    EMSettingsLoaderService,
    KatexCorrectorService,
    LLMSettingsLoaderService,
    MathArticleChunkLoaderService,
    MathArticleLoaderService,
    MathExpressionContextLoaderService,
    MathExpressionDatasetBuilderService,
    MathExpressionDatasetPublisherService,
    MathExpressionDatasetTesterService,
    MathExpressionDescriptionLoaderService,
    MathExpressionDescriptionOptLoaderService,
    MathExpressionGroupLoaderService,
    MathExpressionGroupRelationshipLoaderService,
    MathExpressionIndexBuilderService,
    MathExpressionLabelExporterService,
    MathExpressionLabelLoaderService,
    MathExpressionLabelTaskImporterService,
    MathExpressionLoaderService,
    MathExpressionRelationshipDescriptionLoaderService,
    MathExpressionRelationshipLoaderService,
    MathExpressionSampleLoaderService,
    MMSettingsLoaderService,
)
from math_rag.application.services.backgrounds import (
    FineTuneJobBackgroundService,
    GPUStatsBackgroundService,
    MathExpressionDatasetBackgroundService,
    MathExpressionDatasetTestBackgroundService,
    MathExpressionIndexBackgroundService,
    PBSProResourcesUsedBackgroundService,
    PrometheusSnapshotBackgroundService,
)


class ApplicationContainer(DeclarativeContainer):
    config = Configuration()

    # dependencies
    arxiv_client = Dependency(instance_of=BaseArxivClient)
    katex_client = Dependency(instance_of=BaseKatexClient)
    latex_converter_client = Dependency(instance_of=BaseLatexConverterClient)

    managed_em = Dependency(instance_of=BaseManagedEM)
    managed_llm = Dependency(instance_of=BaseManagedLLM)
    managed_mm = Dependency(instance_of=BaseManagedMM)

    managed_em_scheduler = Dependency(instance_of=BaseBatchEMRequestManagedScheduler)
    managed_llm_scheduler = Dependency(instance_of=BaseBatchLLMRequestManagedScheduler)

    fine_tune_job_repository = Dependency(instance_of=BaseFineTuneJobRepository)
    math_article_chunk_repository = Dependency(instance_of=BaseMathArticleChunkRepository)
    math_expression_index_repository = Dependency(instance_of=BaseMathExpressionIndexRepository)
    math_expression_context_repository = Dependency(instance_of=BaseMathExpressionContextRepository)
    math_expression_dataset_repository = Dependency(instance_of=BaseMathExpressionDatasetRepository)
    math_expression_dataset_test_repository = Dependency(
        instance_of=BaseMathExpressionDatasetTestRepository
    )
    math_expression_dataset_test_result_repository = Dependency(
        instance_of=BaseMathExpressionDatasetTestResultRepository
    )
    math_expression_description_opt_repository = Dependency(
        instance_of=BaseMathExpressionDescriptionOptRepository
    )
    math_expression_description_repository = Dependency(
        instance_of=BaseMathExpressionDescriptionRepository
    )
    math_expression_group_repository = Dependency(instance_of=BaseMathExpressionGroupRepository)
    math_article_repository = Dependency(instance_of=BaseMathArticleRepository)
    math_expression_relationship_description_repository = Dependency(
        instance_of=BaseMathExpressionRelationshipDescriptionRepository
    )
    math_expression_relationship_repository = Dependency(
        instance_of=BaseMathExpressionRelationshipRepository
    )
    math_expression_repository = Dependency(instance_of=BaseMathExpressionRepository)
    math_expression_label_repository = Dependency(instance_of=BaseMathExpressionLabelRepository)
    math_expression_sample_repository = Dependency(instance_of=BaseMathExpressionSampleRepository)
    math_problem_repository = Dependency(instance_of=BaseMathProblemRepository)
    task_repository = Dependency(instance_of=BaseTaskRepository)

    math_expression_description_opt_embedding_repository = Dependency(
        instance_of=BaseMathExpressionDescriptionOptEmbeddingRepository
    )

    math_expression_group_graph_repository = Dependency(
        instance_of=BaseMathExpressionGroupGraphRepository
    )
    math_expression_graph_repository = Dependency(instance_of=BaseMathExpressionGraphRepository)

    grouper_service = Dependency(instance_of=BaseGrouperService)
    dataset_loader_service = Dependency(instance_of=BaseDatasetLoaderService)
    dataset_publisher_service = Dependency(instance_of=BaseDatasetPublisherService)
    gpu_stats_pusher_service = Dependency(instance_of=BaseGPUStatsPusherService)
    math_article_parser_service = Dependency(instance_of=BaseMathArticleParserService)
    label_config_builder_service = Dependency(instance_of=BaseLabelConfigBuilderService)
    label_task_exporter_service = Dependency(instance_of=BaseLabelTaskExporterService)
    label_task_importer_service = Dependency(instance_of=BaseLabelTaskImporterService)
    prometheus_snapshot_loader_service = Dependency(instance_of=BasePrometheusSnapshotLoaderService)
    pbs_pro_resources_used_pusher_service = Dependency(
        instance_of=BasePBSProResoucesUsedPusherService
    )

    fine_tune_job_runner_service = Dependency(instance_of=BaseFineTuneJobRunnerService)

    # non-dependencies
    # assistants
    katex_corrector_assistant = Factory(
        KatexCorrectorAssistant,
        llm=managed_llm,
        scheduler=managed_llm_scheduler,
    )
    katex_corrector_retrier_assistant = Factory(
        KatexCorrectorRetrierAssistant,
        llm=managed_llm,
        scheduler=managed_llm_scheduler,
    )
    math_expression_comparator_assistant = Factory(
        MathExpressionComparatorAssistant,
        llm=managed_llm,
        scheduler=managed_llm_scheduler,
    )
    math_expression_description_optimizer_assistant = Factory(
        MathExpressionDescriptionOptimizerAssistant,
        llm=managed_llm,
        scheduler=managed_llm_scheduler,
    )
    math_expression_description_writer_assistant = Factory(
        MathExpressionDescriptionWriterAssistant,
        llm=managed_llm,
        scheduler=managed_llm_scheduler,
    )
    math_expression_labeler_assistant = Factory(
        MathExpressionLabelerAssistant,
        llm=managed_llm,
        scheduler=managed_llm_scheduler,
    )
    math_expression_relationship_description_writer_assistant = Factory(
        MathExpressionRelationshipDescriptionWriterAssistant,
        llm=managed_llm,
        scheduler=managed_llm_scheduler,
    )
    math_expression_relationship_detector_assistant = Factory(
        MathExpressionRelationshipDetectorAssistant,
        llm=managed_llm,
        scheduler=managed_llm_scheduler,
    )

    # embedders
    default_embedder = Factory(
        DefaultEmbedder,
        em=managed_em,
        scheduler=managed_em_scheduler,
    )

    # moderators
    default_moderator = Factory(
        DefaultModerator,
        mm=managed_mm,
    )

    # services
    em_settings_loader_service = Factory(EMSettingsLoaderService)
    llm_settings_loader_service = Factory(LLMSettingsLoaderService)
    mm_settings_loader_service = Factory(MMSettingsLoaderService)

    math_article_chunk_loader_service = Factory(
        MathArticleChunkLoaderService,
        math_article_parser_service=math_article_parser_service,
        math_article_repository=math_article_repository,
        math_article_chunk_repository=math_article_chunk_repository,
        math_expression_repository=math_expression_repository,
    )
    math_article_loader_service = Factory(
        MathArticleLoaderService,
        arxiv_client=arxiv_client,
        latex_converter_client=latex_converter_client,
        math_article_repository=math_article_repository,
    )

    katex_corrector_service = Factory(
        KatexCorrectorService,
        katex_client=katex_client,
        katex_corrector_assistant=katex_corrector_assistant,
        katex_corrector_retrier_assistant=katex_corrector_retrier_assistant,
    )
    math_expression_loader_service = Factory(
        MathExpressionLoaderService,
        katex_client=katex_client,
        katex_corrector_assistant=katex_corrector_assistant,
        katex_corrector_service=katex_corrector_service,
        math_article_parser_service=math_article_parser_service,
        math_article_repository=math_article_repository,
        math_expression_graph_repository=math_expression_graph_repository,
        math_expression_repository=math_expression_repository,
    )
    math_expression_relationship_description_loader_service = Factory(
        MathExpressionRelationshipDescriptionLoaderService,
        math_expression_relationship_description_writer_assistant=math_expression_relationship_description_writer_assistant,
        math_article_chunk_repository=math_article_chunk_repository,
        math_expression_relationship_description_repository=math_expression_relationship_description_repository,
        math_expression_relationship_repository=math_expression_relationship_repository,
    )
    math_expression_relationship_loader_service = Factory(
        MathExpressionRelationshipLoaderService,
        math_expression_relationship_detector_assistant=math_expression_relationship_detector_assistant,
        math_article_chunk_repository=math_article_chunk_repository,
        math_expression_graph_repository=math_expression_graph_repository,
        math_expression_relationship_repository=math_expression_relationship_repository,
        math_expression_repository=math_expression_repository,
    )
    math_expression_dataset_tester_service = Factory(
        MathExpressionDatasetTesterService,
        dataset_loader_service=dataset_loader_service,
        math_expression_labeler_assistant=math_expression_labeler_assistant,
    )
    math_expression_description_loader_service = Factory(
        MathExpressionDescriptionLoaderService,
        math_expression_description_writer_assistant=math_expression_description_writer_assistant,
        math_article_parser_service=math_article_parser_service,
        math_expression_repository=math_expression_repository,
        math_expression_context_repository=math_expression_context_repository,
        math_expression_description_repository=math_expression_description_repository,
    )
    math_expression_description_opt_loader_service = Factory(
        MathExpressionDescriptionOptLoaderService,
        default_embedder=default_embedder,
        math_expression_description_optimizer_assistant=math_expression_description_optimizer_assistant,
        math_expression_description_repository=math_expression_description_repository,
        math_expression_description_opt_repository=math_expression_description_opt_repository,
        math_expression_description_opt_embedding_repository=math_expression_description_opt_embedding_repository,
    )
    math_expression_group_relationship_loader_service = Factory(
        MathExpressionGroupRelationshipLoaderService,
        math_expression_comparator_assistant=math_expression_comparator_assistant,
        math_expression_context_repository=math_expression_context_repository,
        math_expression_group_graph_repository=math_expression_group_graph_repository,
        math_expression_group_repository=math_expression_group_repository,
        math_expression_graph_repository=math_expression_graph_repository,
        math_expression_repository=math_expression_repository,
    )
    math_expression_group_loader_service = Factory(
        MathExpressionGroupLoaderService,
        math_expression_description_opt_embedding_repository=math_expression_description_opt_embedding_repository,
        math_expression_group_graph_repository=math_expression_group_graph_repository,
        math_expression_group_repository=math_expression_group_repository,
        math_expression_graph_repository=math_expression_graph_repository,
        math_expression_repository=math_expression_repository,
    )
    math_expression_label_loader_service = Factory(
        MathExpressionLabelLoaderService,
        math_expression_labeler_assistant=math_expression_labeler_assistant,
        math_expression_repository=math_expression_repository,
        math_expression_label_repository=math_expression_label_repository,
    )
    math_expression_dataset_publisher_service = Factory(
        MathExpressionDatasetPublisherService,
        math_expression_sample_repository=math_expression_sample_repository,
        dataset_publisher_service=dataset_publisher_service,
    )
    math_expression_sample_loader_service = Factory(
        MathExpressionSampleLoaderService,
        math_expression_sample_repository=math_expression_sample_repository,
    )
    math_expression_context_loader_service = Factory(
        MathExpressionContextLoaderService,
        math_article_parser_service=math_article_parser_service,
        math_article_repository=math_article_repository,
        math_expression_repository=math_expression_repository,
        math_expression_context_repository=math_expression_context_repository,
    )
    math_expression_dataset_builder_service = Factory(
        MathExpressionDatasetBuilderService,
        math_article_loader_service=math_article_loader_service,
        math_expression_dataset_publisher_service=math_expression_dataset_publisher_service,
        math_expression_dataset_repository=math_expression_dataset_repository,
        math_expression_label_loader_service=math_expression_label_loader_service,
        math_expression_loader_service=math_expression_loader_service,
        math_expression_sample_loader_service=math_expression_sample_loader_service,
    )
    math_expression_index_builder_service = Factory(
        MathExpressionIndexBuilderService,
        math_article_chunk_loader_service=math_article_chunk_loader_service,
        math_article_loader_service=math_article_loader_service,
        math_expression_context_loader_service=math_expression_context_loader_service,
        math_expression_description_loader_service=math_expression_description_loader_service,
        math_expression_description_opt_loader_service=math_expression_description_opt_loader_service,
        math_expression_group_loader_service=math_expression_group_loader_service,
        math_expression_group_relationship_loader_service=math_expression_group_relationship_loader_service,
        math_expression_label_loader_service=math_expression_label_loader_service,
        math_expression_loader_service=math_expression_loader_service,
        math_expression_relationship_description_loader_service=math_expression_relationship_description_loader_service,
        math_expression_relationship_loader_service=math_expression_relationship_loader_service,
        math_expression_index_repository=math_expression_index_repository,
    )

    math_expression_label_exporter_service = Factory(
        MathExpressionLabelExporterService,
        label_task_exporter_service=label_task_exporter_service,
    )
    math_expression_label_task_importer_service = Factory(
        MathExpressionLabelTaskImporterService,
        dataset_loader_service=dataset_loader_service,
        katex_client=katex_client,
        label_config_builder_service=label_config_builder_service,
        label_task_importer_service=label_task_importer_service,
    )

    # background services
    fine_tune_job_background_service = Singleton(
        FineTuneJobBackgroundService,
        fine_tune_job_runner_service=fine_tune_job_runner_service,
        fine_tune_job_repository=fine_tune_job_repository,
        task_repository=task_repository,
    )
    gpu_stats_background_service = Singleton(
        GPUStatsBackgroundService, gpu_stats_pusher_service=gpu_stats_pusher_service
    )
    math_expression_index_background_service = Singleton(
        MathExpressionIndexBackgroundService,
        math_expression_index_builder_service=math_expression_index_builder_service,
        math_expression_index_repository=math_expression_index_repository,
        task_repository=task_repository,
    )
    math_expression_dataset_background_service = Singleton(
        MathExpressionDatasetBackgroundService,
        math_expression_dataset_builder_service=math_expression_dataset_builder_service,
        math_expression_dataset_repository=math_expression_dataset_repository,
        task_repository=task_repository,
    )
    math_expression_dataset_test_background_service = Singleton(
        MathExpressionDatasetTestBackgroundService,
        math_expression_dataset_tester_service=math_expression_dataset_tester_service,
        math_expression_dataset_test_repository=math_expression_dataset_test_repository,
        math_expression_dataset_test_result_repository=math_expression_dataset_test_result_repository,
        task_repository=task_repository,
    )
    pbs_pro_resources_used_background_service = Singleton(
        PBSProResourcesUsedBackgroundService,
        pbs_pro_resources_used_pusher_service=pbs_pro_resources_used_pusher_service,
    )
    prometheus_snapshot_background_service = Singleton(
        PrometheusSnapshotBackgroundService,
        prometheus_snapshot_loader_service=prometheus_snapshot_loader_service,
    )

    background_services: Provider[list[BaseBackgroundService]] = List(
        fine_tune_job_background_service,
        gpu_stats_background_service,
        math_expression_index_background_service,
        math_expression_dataset_background_service,
        math_expression_dataset_test_background_service,
        pbs_pro_resources_used_background_service,
        # prometheus_snapshot_background_service,   # NOTE: not needed at the moment
    )
