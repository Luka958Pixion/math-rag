from asyncio import gather
from io import BytesIO
from logging import getLogger
from pathlib import Path
from uuid import UUID, uuid4
from zipfile import ZipFile

from arxiv import Result
from httpx import AsyncClient

from math_rag.application.base.clients import BaseArxivClient, BaseLatexConverterClient
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import BaseMathArticleLoaderService
from math_rag.application.constants import DOWNLOADS_DIR_PATH
from math_rag.application.utils import MagicBytesWriterUtil
from math_rag.core.models import MathArticle, MathExpressionDataset, MathExpressionIndex
from math_rag.core.types import ArxivCategoryType
from math_rag.shared.utils import GzipExtractorUtil


BATCH_SIZE = 5

logger = getLogger(__name__)


class MathArticleLoaderService(BaseMathArticleLoaderService):
    def __init__(
        self,
        arxiv_client: BaseArxivClient,
        latex_converter_client: BaseLatexConverterClient,
        math_article_repository: BaseMathArticleRepository,
    ):
        self.arxiv_client = arxiv_client
        self.latex_converter_client = latex_converter_client
        self.math_article_repository = math_article_repository

    async def load_for_dataset(
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
        logger.info(f'{self.__class__.__name__} loaded {num_math_articles} math articles in total')

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

    async def load_for_index(self, index: MathExpressionIndex):
        if index.build_details.url and '/api/v1/download-shared-object' in index.build_details.url:
            async with AsyncClient() as client:
                url = index.build_details.url.replace('localhost', 'minio')  # NOTE: not clean
                response = await client.get(url)
                response.raise_for_status()

            index.build_details.file_path = await MagicBytesWriterUtil.write(
                response.content,
                DOWNLOADS_DIR_PATH,
                allowed_content_types=self.latex_converter_client.list_content_types(),
            )
            index.build_details.url = None

        path = index.build_details.file_path
        url = index.build_details.url

        if (path and path.suffix != '.pdf') or (url and not url.endswith('.pdf')):
            raise ValueError()

        tex_zip_bytes = self.latex_converter_client.convert_pdf(file_path=path, url=url)
        id = uuid4()
        tex_zip_path = DOWNLOADS_DIR_PATH / f'{id.hex}.zip'
        tex_zip = self._extract_tex_zip(tex_zip_bytes, tex_zip_path)
        tex_file_name, tex_file_bytes = self._read_tex_file(tex_zip)

        math_article = MathArticle(
            math_expression_dataset_id=None,
            math_expression_index_id=index.id,
            name=tex_file_name,
            bytes=tex_file_bytes,
        )
        await self.math_article_repository.insert_one(math_article)
        logger.info(f'{self.__class__.__name__} loaded a math article from {path}')

    def _extract_tex_zip(self, zip_bytes: bytes, file_path: Path) -> Path:
        dir_path = file_path.parent / file_path.stem
        dir_path.mkdir(parents=True, exist_ok=True)

        with ZipFile(BytesIO(zip_bytes)) as zip_file:
            zip_file.extractall(dir_path)

        return dir_path

    def _read_tex_file(self, dir_path: Path) -> tuple[str, bytes]:
        nested_dir = next(path for path in dir_path.iterdir() if path.is_dir())
        tex_file = next(path for path in nested_dir.iterdir() if path.suffix == '.tex')

        return tex_file.name, tex_file.read_bytes()
