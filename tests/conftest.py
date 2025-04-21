import pytest

from math_rag.application.containers import ApplicationContainer
from math_rag.infrastructure.containers import InfrastructureContainer


@pytest.fixture(scope='session')
def application_container() -> ApplicationContainer:
    container = ApplicationContainer()
    container.init_resources()

    return container


@pytest.fixture(scope='session')
def infrastructure_container() -> InfrastructureContainer:
    container = InfrastructureContainer()
    container.init_resources()

    return container
