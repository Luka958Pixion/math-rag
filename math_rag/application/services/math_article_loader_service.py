from asyncio import gather
from logging import getLogger
from uuid import UUID

from arxiv import Result

from math_rag.application.base.clients import BaseArxivClient
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import BaseMathArticleLoaderService
from math_rag.core.models import MathArticle, MathExpressionDataset
from math_rag.core.types import ArxivCategoryType
from math_rag.shared.utils import GzipExtractorUtil


logger = getLogger(__name__)
BATCH_SIZE = 5


class MathArticleLoaderService(BaseMathArticleLoaderService):
    def __init__(
        self,
        arxiv_client: BaseArxivClient,
        math_article_repository: BaseMathArticleRepository,
    ):
        self.arxiv_client = arxiv_client
        self.math_article_repository = math_article_repository

    async def load(
        self,
        dataset: MathExpressionDataset,
        *,
        categories: list[ArxivCategoryType],
        category_limit: int,
    ):
        num_math_articles = 0

        for category in categories:
            num_math_articles += await self._process_arxiv_category(
                dataset.id, category, category_limit
            )

        self.math_article_repository.backup()
        logger.info(f'{self.__class__.__name__} {num_math_articles} math articles in total')

    async def _process_arxiv_category(
        self, dataset_id: UUID, category: ArxivCategoryType, category_limit: int
    ) -> int:
        files = await self._search(category, category_limit, max_num_retries=10)
        math_articles = [
            MathArticle(
                math_expression_dataset_id=dataset_id,
                math_expression_index_id=None,
                name=name,
                bytes=bytes,
            )
            for file in files
            for name, bytes in file.items()
        ]
        await self.math_article_repository.insert_many(math_articles)
        logger.info(f'{self.__class__.__name__} loaded {len(math_articles)} math articles')

        return len(math_articles)

    async def _search(
        self, category: str, category_limit: int, *, max_num_retries: int
    ) -> list[dict[str, bytes]]:
        new_category_limit = category_limit
        num_retries = 0

        while num_retries < max_num_retries:
            results = self.arxiv_client.search(
                category, new_category_limit * 10, (new_category_limit - 1) * 10
            )
            process_tasks = [self._process_result(result) for result in results]
            processed_files = await gather(*process_tasks)

            # filter out None and count how many were None
            files = [file for file in processed_files if file is not None]
            num_files = len(files)
            num_nones = category_limit - num_files

            if num_files >= category_limit:
                return files[:category_limit]

            new_category_limit += num_nones
            num_retries += 1

        raise RuntimeError(
            f'Could not retrieve {category_limit} processed files for '
            f'category {category} after {max_num_retries} retries'
        )

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
