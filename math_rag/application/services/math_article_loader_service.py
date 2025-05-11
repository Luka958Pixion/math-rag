from math_rag.application.base.clients import BaseArxivClient
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import BaseMathArticleLoaderService
from math_rag.application.enums.arxiv import BaseArxivCategory
from math_rag.core.models import MathArticle
from math_rag.shared.utils import GzipExtractorUtil


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

        sublimit = int(limit / len(BaseArxivCategory))
        results = [
            result
            for subcategory in category
            for result in self.arxiv_client.search(subcategory, sublimit)
        ]
        file_name_to_bytes: dict[str, bytes] = {}

        for result in results:
            arxiv_id = result.entry_id.split('/')[-1]
            src = await self.arxiv_client.get_src(arxiv_id)
            # NOTE: we dont need pdfs at the moment
            # pdf = await arxiv_searcher_service.get_pdf(arxiv_id)

            if src is None:
                continue

            src_name, src_bytes = src

            if not src_name or src_name.endswith('.pdf'):
                continue

            if src_name.endswith('.tar.gz'):
                extracted_file_to_bytes = GzipExtractorUtil.extract_tar_gz(src_bytes)
                file_name_to_bytes.update(
                    {f'{arxiv_id}/{k}': v for k, v in extracted_file_to_bytes.items()}
                )

            elif src_name.endswith('.gz'):
                extracted_bytes = GzipExtractorUtil.extract_gz(src_bytes)
                file_name_to_bytes[f'{arxiv_id}.tex'] = extracted_bytes

            else:
                raise ValueError(f'Unexpected file extension {src_name}')

        math_articles = [
            MathArticle(name=name, bytes=bytes)
            for name, bytes in file_name_to_bytes.items()
        ]
        self.math_article_repository.insert_many(math_articles)
