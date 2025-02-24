from math_rag.infrastructure.containers import InfrastructureContainer


def main():
    infrastructure_container = InfrastructureContainer()
    infrastructure_container.wire(modules=[__name__])

    minio_client = infrastructure_container.minio_client()
    math_article_repository = infrastructure_container.math_article_repository(
        client=minio_client
    )


if __name__ == '__main__':
    main()
