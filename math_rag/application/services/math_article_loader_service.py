from math_rag.application.base.clients import BaseArxivClient
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.enums.arxiv import MathCategory
from math_rag.core.models import MathArticle
from math_rag.shared.utils import GzipExtractorUtil


class MathArticleLoaderService:
    def __init__(
        self,
        arxiv_client: BaseArxivClient,
        math_article_repository: BaseMathArticleRepository,
    ):
        self.arxiv_client = arxiv_client
        self.math_article_repository = math_article_repository

    async def load(self):
        results = [
            result
            for category in MathCategory
            for result in self.arxiv_client.search(category, 4)
        ]
        files: dict[str, bytes] = {}

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
                extracted_files = GzipExtractorUtil.extract_tar_gz(src_bytes)
                files.update({f'{arxiv_id}/{k}': v for k, v in extracted_files.items()})

            elif src_name.endswith('.gz'):
                extracted_bytes = GzipExtractorUtil.extract_gz(src_bytes)
                files[f'{arxiv_id}.tex'] = extracted_bytes

            else:
                raise ValueError(f'Unexpected file extension {src_name}')

        math_articles = [
            MathArticle(name=name, bytes=bytes) for name, bytes in files.items()
        ]
        self.math_article_repository.insert_many(math_articles)
