from arxiv import Client, Result, Search, SortCriterion, SortOrder
from httpx import AsyncClient, HTTPStatusError, RequestError

from .arxiv import (
    BaseArxivCategory,
    CompSciCategory,
    EconCategory,
    EESSCategory,
    MathCategory,
    PhysCategory,
    QuantBioCategory,
    QuantFinCategory,
    StatsCategory,
)


CATEGORY_TYPE_TO_PREFIX: dict[type[BaseArxivCategory], str] = {
    CompSciCategory: 'cs',
    EconCategory: 'econ',
    EESSCategory: 'eess',
    MathCategory: 'math',
    QuantBioCategory: 'q-bio',
    QuantFinCategory: 'q-fin',
    StatsCategory: 'stat',
}


class ArxivSearcherService:
    def search(self, category: BaseArxivCategory, limit: int) -> list[Result]:
        category_name = self._get_category_name(category)
        subcategory_name = self._get_subcategory_name(category)
        query = f'cat:{category_name}.{subcategory_name or str()}'

        search = Search(
            query=query,
            max_results=limit,
            sort_by=SortCriterion.SubmittedDate,
            sort_order=SortOrder.Descending,
        )
        client = Client()
        results = client.results(search)

        return list(results)

    async def get_pdf(self, entry_id: str) -> tuple[str, bytes] | None:
        url = f'https://arxiv.org/pdf/{entry_id}.pdf'

        return await self._fetch_file(url)

    async def get_src(self, entry_id: str) -> tuple[str, bytes] | None:
        url = f'https://arxiv.org/src/{entry_id}'

        return await self._fetch_file(url)

    def _get_category_name(self, category: BaseArxivCategory) -> str:
        if type(category) == PhysCategory:
            return category.name.lower()

        return CATEGORY_TYPE_TO_PREFIX[type(category)]

    def _get_subcategory_name(self, category: BaseArxivCategory) -> str | None:
        if category in [
            PhysCategory.GR_QC,
            PhysCategory.HEP_EX,
            PhysCategory.HEP_LAT,
            PhysCategory.HEP_PH,
            PhysCategory.HEP_TH,
            PhysCategory.MATH_PH,
            PhysCategory.NUCL_EX,
            PhysCategory.NUCL_TH,
            PhysCategory.QUANT_PH,
        ]:
            return None

        if category in [PhysCategory.COND_MAT, PhysCategory.PHYSICS]:
            return category.name.lower()

        return category.name

    async def _fetch_file(self, url: str) -> tuple[str, bytes] | None:
        try:
            async with AsyncClient(follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()

        except (RequestError, HTTPStatusError):
            return None

        disposition = str(response.headers.get('Content-Disposition', ''))
        filename = disposition.partition('filename=')[2].strip('"')

        return filename, response.content
