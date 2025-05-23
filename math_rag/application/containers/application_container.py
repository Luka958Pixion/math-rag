from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    Dependency,
    Factory,
    Provider,
    Singleton,
)

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.contexts import IndexBuildContext
from math_rag.application.services import (
    EMSettingsLoaderService,
    IndexBuilderService,
    IndexBuildTrackerService,
    LLMSettingsLoaderService,
)


class ApplicationContainer(DeclarativeContainer):
    config = Configuration()

    em_settings_loader_service = Factory(EMSettingsLoaderService)
    llm_settings_loader_service = Factory(LLMSettingsLoaderService)

    index_repository: Provider[BaseIndexRepository] = Dependency()

    index_builder_service = Singleton(IndexBuilderService)
    index_build_context = Singleton(IndexBuildContext)
    index_build_tracker_service = Singleton(
        IndexBuildTrackerService,
        index_repository=index_repository,
        index_builder_service=index_builder_service,
        index_build_context=index_build_context,
    )
