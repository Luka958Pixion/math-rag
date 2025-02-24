from math_rag.infrastructure.containers import InfrastructureContainer


async def main():
    infrastructure_container = InfrastructureContainer()
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
    main()
