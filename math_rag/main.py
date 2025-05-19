from asyncio import run
from logging import ERROR, INFO, basicConfig, getLogger

from math_rag.application.containers import ApplicationContainer
from math_rag.infrastructure.containers import InfrastructureContainer


basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
getLogger('pylatexenc.latexwalker').setLevel(ERROR)


async def main():
    application_container = ApplicationContainer()
    application_container.init_resources()
    application_container.wire(modules=[__name__])

    infrastructure_container = InfrastructureContainer()
    infrastructure_container.application_container.override(application_container)
    infrastructure_container.init_resources()
    infrastructure_container.wire(modules=[__name__])

    # Minio
    math_article_seeder = infrastructure_container.math_article_seeder()
    await math_article_seeder.seed()

    # Mongo
    math_expression_seeder = infrastructure_container.math_expression_seeder()
    await math_expression_seeder.seed()

    # Neo4j

    # Qdrant


if __name__ == '__main__':
    run(main())
