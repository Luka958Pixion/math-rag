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
from math_rag.application.base.clients import BaseArxivClient, BaseKatexClient
from math_rag.application.base.inference import (
    BaseBatchLLMRequestManagedScheduler,
    BaseManagedLLM,
)
from math_rag.application.base.repositories.documents import (
    BaseDatasetRepository,
    BaseIndexRepository,
    BaseMathExpressionLabelRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import (
    BaseLatexParserService,
    BaseLatexVisitorService,
)
from math_rag.application.contexts import DatasetBuildContext, IndexBuildContext
from math_rag.application.services import (
    DatasetBuilderService,
    EMSettingsLoaderService,
    IndexBuilderService,
    LLMSettingsLoaderService,
    MathArticleLoaderService,
    MathArticleParserService,
    MathExpressionLabelLoaderService,
    MathExpressionLoaderService,
)
from math_rag.application.services.background import (
    DatasetBuildTrackerBackgroundService,
    IndexBuildTrackerBackgroundService,
)


class ApplicationContainer(DeclarativeContainer):
    config = Configuration()

    # dependencies
    arxiv_client: Provider[BaseArxivClient] = Dependency()
    katex_client: Provider[BaseKatexClient] = Dependency()

    managed_llm: Provider[BaseManagedLLM] = Dependency()
    managed_scheduler: Provider[BaseBatchLLMRequestManagedScheduler] = Dependency()

    latex_parser_service: Provider[BaseLatexParserService] = Dependency()
    latex_visitor_service: Provider[BaseLatexVisitorService] = Dependency()

    index_repository: Provider[BaseIndexRepository] = Dependency()
    dataset_repository: Provider[BaseDatasetRepository] = Dependency()
    math_article_repository: Provider[BaseMathArticleRepository] = Dependency()
    math_expression_repository: Provider[BaseMathExpressionRepository] = Dependency()
    math_expression_label_repository: Provider[BaseMathExpressionLabelRepository] = (
        Dependency()
    )

    # non-dependencies
    katex_corrector_assistant = Factory(
        KatexCorrectorAssistant, llm=managed_llm, scheduler=managed_scheduler
    )
    math_expression_labeler_assistant = Factory(
        MathExpressionLabelerAssistant, llm=managed_llm, scheduler=managed_scheduler
    )

    em_settings_loader_service = Factory(EMSettingsLoaderService)
    llm_settings_loader_service = Factory(LLMSettingsLoaderService)
    math_article_parser_service = Factory(
        MathArticleParserService,
        latex_parser_service=latex_parser_service,
        latex_visitor_service=latex_visitor_service,
    )
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
    math_expression_label_loader_service = Factory(
        MathExpressionLabelLoaderService,
        math_expression_labeler_assistant=math_expression_labeler_assistant,
        math_expression_repository=math_expression_repository,
        math_expression_label_repository=math_expression_label_repository,
    )
    dataset_builder_service = Factory(
        DatasetBuilderService,
        math_article_loader_service=math_article_loader_service,
        math_expression_loader_service=math_expression_loader_service,
        math_expression_label_loader_service=math_expression_label_loader_service,
        dataset_repository=dataset_repository,
    )
    dataset_build_context = Singleton(DatasetBuildContext)
    dataset_build_tracker_background_service = Singleton(
        DatasetBuildTrackerBackgroundService,
        dataset_repository=dataset_repository,
        dataset_builder_service=dataset_builder_service,
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
