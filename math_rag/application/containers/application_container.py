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
    MathExpressionLabelerAssistant,
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
)
from math_rag.application.base.repositories.documents import (
    BaseFineTuneJobRepository,
    BaseIndexRepository,
    BaseMathExpressionDatasetRepository,
    BaseMathExpressionDatasetTestRepository,
    BaseMathExpressionLabelRepository,
    BaseMathExpressionRepository,
    BaseMathExpressionSampleRepository,
    BaseMathProblemRepository,
    BaseTaskRepository,
)
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import (
    BaseDatasetLoaderService,
    BaseDatasetPublisherService,
    BaseLabelConfigBuilderService,
    BaseLabelTaskExporterService,
    BaseLabelTaskImporterService,
    BaseMathArticleParserService,
    BasePrometheusSnapshotLoaderService,
)
from math_rag.application.base.services.backgrounds import BaseBackgroundService
from math_rag.application.embedants import MathExpressionDescriptionEmbedant
from math_rag.application.services import (
    EMSettingsLoaderService,
    IndexBuilderService,
    LLMSettingsLoaderService,
    MathArticleLoaderService,
    MathExpressionDatasetBuilderService,
    MathExpressionDatasetPublisherService,
    MathExpressionDatasetTesterService,
    MathExpressionLabelExporterService,
    MathExpressionLabelLoaderService,
    MathExpressionLabelTaskImporterService,
    MathExpressionLoaderService,
    MathExpressionSampleLoaderService,
)
from math_rag.application.services.backgrounds import (
    FineTuneJobBackgroundService,
    IndexBackgroundService,
    MathExpressionDatasetBackgroundService,
    MathExpressionDatasetTestBackgroundService,
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

    managed_em_scheduler = Dependency(instance_of=BaseBatchEMRequestManagedScheduler)
    managed_llm_scheduler = Dependency(instance_of=BaseBatchLLMRequestManagedScheduler)

    fine_tune_job_repository = Dependency(instance_of=BaseFineTuneJobRepository)
    index_repository = Dependency(instance_of=BaseIndexRepository)
    math_expression_dataset_repository = Dependency(instance_of=BaseMathExpressionDatasetRepository)
    math_expression_dataset_test_repository = Dependency(
        instance_of=BaseMathExpressionDatasetTestRepository
    )
    math_article_repository = Dependency(instance_of=BaseMathArticleRepository)
    math_expression_repository = Dependency(instance_of=BaseMathExpressionRepository)
    math_expression_label_repository = Dependency(instance_of=BaseMathExpressionLabelRepository)
    math_expression_sample_repository = Dependency(instance_of=BaseMathExpressionSampleRepository)
    math_problem_repository = Dependency(instance_of=BaseMathProblemRepository)
    task_repository = Dependency(instance_of=BaseTaskRepository)

    dataset_loader_service = Dependency(instance_of=BaseDatasetLoaderService)
    dataset_publisher_service = Dependency(instance_of=BaseDatasetPublisherService)
    math_article_parser_service = Dependency(instance_of=BaseMathArticleParserService)
    label_config_builder_service = Dependency(instance_of=BaseLabelConfigBuilderService)
    label_task_exporter_service = Dependency(instance_of=BaseLabelTaskExporterService)
    label_task_importer_service = Dependency(instance_of=BaseLabelTaskImporterService)
    prometheus_snapshot_loader_service = Dependency(instance_of=BasePrometheusSnapshotLoaderService)

    fine_tune_job_runner_service = Dependency(instance_of=BaseFineTuneJobRunnerService)

    # non-dependencies
    katex_corrector_assistant = Factory(
        KatexCorrectorAssistant, llm=managed_llm, scheduler=managed_llm_scheduler
    )
    math_expression_labeler_assistant = Factory(
        MathExpressionLabelerAssistant, llm=managed_llm, scheduler=managed_llm_scheduler
    )

    math_expression_description_embedant = Factory(
        MathExpressionDescriptionEmbedant,
        em=managed_em,
        scheduler=managed_em_scheduler,
    )

    em_settings_loader_service = Factory(EMSettingsLoaderService)
    llm_settings_loader_service = Factory(LLMSettingsLoaderService)
    math_article_loader_service = Factory(
        MathArticleLoaderService,
        arxiv_client=arxiv_client,
        math_article_repository=math_article_repository,
    )
    math_expression_loader_service = Factory(
        MathExpressionLoaderService,
        katex_client=katex_client,
        katex_corrector_assistant=katex_corrector_assistant,
        math_article_parser_service=math_article_parser_service,
        math_article_repository=math_article_repository,
        math_expression_repository=math_expression_repository,
    )
    math_expression_dataset_tester_service = Factory(
        MathExpressionDatasetTesterService,
        dataset_loader_service=dataset_loader_service,
        math_expression_labeler_assistant=math_expression_labeler_assistant,
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

    math_expression_dataset_builder_service = Factory(
        MathExpressionDatasetBuilderService,
        math_article_loader_service=math_article_loader_service,
        math_expression_loader_service=math_expression_loader_service,
        math_expression_label_loader_service=math_expression_label_loader_service,
        math_expression_sample_loader_service=math_expression_sample_loader_service,
        math_expression_dataset_publisher_service=math_expression_dataset_publisher_service,
        math_expression_dataset_repository=math_expression_dataset_repository,
    )
    index_builder_service = Factory(
        IndexBuilderService,
        math_article_loader_service=math_article_loader_service,
        math_expression_loader_service=math_expression_loader_service,
        math_expression_label_loader_service=math_expression_label_loader_service,
        index_repository=index_repository,
    )

    math_expression_label_exporter_service = Factory(
        MathExpressionLabelExporterService, label_task_exporter_service=label_task_exporter_service
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
    index_background_service = Singleton(
        IndexBackgroundService,
        index_builder_service=index_builder_service,
        index_repository=index_repository,
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
        task_repository=task_repository,
    )
    prometheus_snapshot_background_service = Singleton(
        PrometheusSnapshotBackgroundService,
        prometheus_snapshot_loader_service=prometheus_snapshot_loader_service,
    )

    background_services: Provider[list[BaseBackgroundService]] = List(
        fine_tune_job_background_service,
        index_background_service,
        math_expression_dataset_background_service,
        math_expression_dataset_test_background_service,
        prometheus_snapshot_background_service,
    )
