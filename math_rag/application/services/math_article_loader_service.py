from asyncio import gather
from logging import getLogger
from uuid import UUID

from arxiv import Result

from math_rag.application.base.clients import BaseArxivClient
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import BaseMathArticleLoaderService
from math_rag.application.types.arxiv import ArxivCategoryType
from math_rag.core.models import MathArticle
from math_rag.shared.utils import GzipExtractorUtil


logger = getLogger(__name__)
BATCH_SIZE = 5


class MathArticleDatasetLoaderService(BaseMathArticleLoaderService):
    def __init__(
        self,
        arxiv_client: BaseArxivClient,
        math_article_repository: BaseMathArticleRepository,
    ):
        self.arxiv_client = arxiv_client
        self.math_article_repository = math_article_repository

    async def load(
        self,
        dataset_id: UUID,
        *,
        arxiv_category_type: type[ArxivCategoryType] | None = None,
        arxiv_category: ArxivCategoryType | None = None,
        limit: int,
    ):
        if arxiv_category_type:
            arxiv_categories = list(arxiv_category_type)

        elif arxiv_category:
            arxiv_categories = [arxiv_category]

        else:
            raise ValueError()

        num_math_articles = 0

        for category in arxiv_categories:
            num_math_articles += await self._process_arxiv_category(dataset_id, category, limit)

        self.math_article_repository.backup()
        logger.info(f'{self.__class__.__name__} {num_math_articles} math articles in total')

    async def _process_arxiv_category(
        self, dataset_id: UUID, arxiv_category: ArxivCategoryType, limit: int
    ) -> int:
        results = self.arxiv_client.search(arxiv_category, limit)
        process_tasks = [self._process_result(result) for result in results]
        processed_files = await gather(*process_tasks)
        math_articles = [
            MathArticle(
                math_expression_dataset_id=dataset_id, index_id=None, name=name, bytes=bytes
            )
            for file in processed_files
            if file
            for name, bytes in file.items()
        ]
        self.math_article_repository.insert_many(math_articles)
        logger.info(f'{self.__class__.__name__} loaded {len(math_articles)} math articles')

    async def _process_result(self, result: Result) -> dict[str, bytes] | None:
        arxiv_id = result.entry_id.split('/')[-1]
        src = await self.arxiv_client.get_src(arxiv_id)

        if src is None:
            return None

        src_name, src_bytes = src

        if not src_name or src_name.endswith('.pdf'):
            return None

        if src_name.endswith('.tar.gz'):
            extracted_file_to_bytes = GzipExtractorUtil.extract_tar_gz(src_bytes)

            return {f'{arxiv_id}/{key}': value for key, value in extracted_file_to_bytes.items()}

        if src_name.endswith('.gz'):
            extracted_bytes = GzipExtractorUtil.extract_gz(src_bytes)

            return {f'{arxiv_id}.tex': extracted_bytes}

        raise ValueError(f'Unexpected file extension {src_name}')
