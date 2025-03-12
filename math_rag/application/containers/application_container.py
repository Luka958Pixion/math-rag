from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration

from math_rag.application.services import SettingsLoaderService


class ApplicationContainer(DeclarativeContainer):
    config = Configuration()

    settings_loader_service = SettingsLoaderService()
