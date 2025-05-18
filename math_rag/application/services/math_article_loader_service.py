from asyncio import gather

from arxiv import Result

from math_rag.application.base.clients import BaseArxivClient
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import BaseMathArticleLoaderService
from math_rag.application.enums.arxiv import BaseArxivCategory
from math_rag.core.models import MathArticle
from math_rag.shared.utils import GzipExtractorUtil


BATCH_SIZE = 5


class MathArticleLoaderService(BaseMathArticleLoaderService):
    def __init__(
        self,
        arxiv_client: BaseArxivClient,
        math_article_repository: BaseMathArticleRepository,
    ):
        self.arxiv_client = arxiv_client
        self.math_article_repository = math_article_repository

    async def load(self, category: BaseArxivCategory, limit: int):
        if limit < len(BaseArxivCategory):
            raise ValueError()

        sublimit = int(limit / len(category))
        category_list = list(category)

        for i in range(0, len(category_list), BATCH_SIZE):
            batch = category_list[i : i + BATCH_SIZE]
            results = [
                result
                for subcategory in batch
                for result in self.arxiv_client.search(subcategory, sublimit)
            ]
            process_tasks = [self._process_result(result) for result in results]
            processed_files = await gather(*process_tasks)
            math_articles = [
                MathArticle(name=name, bytes=bytes)
                for d in processed_files
                if d
                for name, bytes in d.items()
            ]
            self.math_article_repository.insert_many(math_articles)

        self.math_article_repository.backup()

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

            return {
                f'{arxiv_id}/{key}': value
                for key, value in extracted_file_to_bytes.items()
            }

        if src_name.endswith('.gz'):
            extracted_bytes = GzipExtractorUtil.extract_gz(src_bytes)

            return {f'{arxiv_id}.tex': extracted_bytes}

        raise ValueError(f'Unexpected file extension {src_name}')
