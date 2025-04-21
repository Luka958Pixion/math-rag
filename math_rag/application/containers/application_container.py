from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory

from math_rag.application.services import (
    EMSettingsLoaderService,
    LLMSettingsLoaderService,
)


class ApplicationContainer(DeclarativeContainer):
    config = Configuration()

    em_settings_loader_service = Factory(EMSettingsLoaderService)
    llm_settings_loader_service = Factory(LLMSettingsLoaderService)
