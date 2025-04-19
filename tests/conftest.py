import pytest

from math_rag.infrastructure.containers import InfrastructureContainer


@pytest.fixture(scope='session')
def infrastructure_container() -> InfrastructureContainer:
    container = InfrastructureContainer()
    container.init_resources()

    return container
