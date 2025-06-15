from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    Dependency,
    Factory,
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
    BaseMathExpressionLabelRepository,
    BaseMathExpressionRepository,
    BaseMathExpressionSampleRepository,
    BaseMathProblemRepository,
)
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import (
    BaseDatasetLoaderService,
    BaseDatasetPublisherService,
    BaseMathArticleParserService,
)
from math_rag.application.contexts import DatasetBuildContext, IndexBuildContext
from math_rag.application.embedants import MathExpressionDescriptionEmbedant
from math_rag.application.services import (
    EMSettingsLoaderService,
    IndexBuilderService,
    LLMSettingsLoaderService,
    MathArticleDatasetLoaderService,
    MathExpressionDatasetBuilderService,
    MathExpressionDatasetPublisherService,
    MathExpressionLabelLoaderService,
    MathExpressionLoaderService,
    MathExpressionSampleLoaderService,
)
from math_rag.application.services.background import (
    IndexBuildTrackerBackgroundService,
    MathExpressionDatasetBuildTrackerBackgroundService,
)


class ApplicationContainer(DeclarativeContainer):
    config = Configuration()

    # dependencies
    arxiv_client: Provider[BaseArxivClient] = Dependency()
    katex_client: Provider[BaseKatexClient] = Dependency()
    latex_converter_client: Provider[BaseLatexConverterClient] = Dependency()

    managed_em: Provider[BaseManagedEM] = Dependency()
    managed_llm: Provider[BaseManagedLLM] = Dependency()

    managed_em_scheduler: Provider[BaseBatchEMRequestManagedScheduler] = Dependency()
    managed_llm_scheduler: Provider[BaseBatchLLMRequestManagedScheduler] = Dependency()

    fine_tune_job_repository: Provider[BaseFineTuneJobRepository] = Dependency()
    index_repository: Provider[BaseIndexRepository] = Dependency()
    math_expression_dataset_repository: Provider[BaseMathExpressionDatasetRepository] = Dependency()
    math_article_repository: Provider[BaseMathArticleRepository] = Dependency()
    math_expression_repository: Provider[BaseMathExpressionRepository] = Dependency()
    math_expression_label_repository: Provider[BaseMathExpressionLabelRepository] = Dependency()
    math_expression_sample_repository: Provider[BaseMathExpressionSampleRepository] = Dependency()
    math_problem_repository: Provider[BaseMathProblemRepository] = Dependency()

    dataset_loader_service: Provider[BaseDatasetLoaderService] = Dependency()
    dataset_publisher_service: Provider[BaseDatasetPublisherService] = Dependency()
    math_article_parser_service: Provider[BaseMathArticleParserService] = Dependency()

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
        MathArticleDatasetLoaderService,
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
    dataset_build_context = Singleton(DatasetBuildContext)
    dataset_build_tracker_background_service = Singleton(
        MathExpressionDatasetBuildTrackerBackgroundService,
        math_expression_dataset_repository=math_expression_dataset_repository,
        math_expression_dataset_builder_service=math_expression_dataset_builder_service,
        dataset_build_context=dataset_build_context,
    )

    index_builder_service = Factory(
        IndexBuilderService,
        math_article_loader_service=math_article_loader_service,
        math_expression_loader_service=math_expression_loader_service,
        math_expression_label_loader_service=math_expression_label_loader_service,
        index_repository=index_repository,
    )
    index_build_context = Singleton(IndexBuildContext)
    index_build_tracker_background_service = Singleton(
        IndexBuildTrackerBackgroundService,
        index_repository=index_repository,
        index_builder_service=index_builder_service,
        index_build_context=index_build_context,
    )
