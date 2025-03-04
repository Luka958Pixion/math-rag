from arxiv import Client, Result, Search, SortCriterion, SortOrder

from math_rag.core.base import BaseCategory
from math_rag.core.enums.categories import (
    CompSciCategory,
    EconCategory,
    EESSCategory,
    MathCategory,
    PhysCategory,
    QuantBioCategory,
    QuantFinCategory,
    StatsCategory,
)


CATEGORY_TYPE_TO_PREFIX: dict[type[BaseCategory], str] = {
    CompSciCategory: 'cs',
    EconCategory: 'econ',
    EESSCategory: 'eess',
    MathCategory: 'math',
    QuantBioCategory: 'q-bio',
    QuantFinCategory: 'q-fin',
    StatsCategory: 'stat',
}


class ArxivSearcherService:
    def search(self, category: BaseCategory, limit: int) -> list[Result]:
        category_name = self.get_category_name(category)
        subcategory_name = self.get_subcategory_name(category)
        query = f'cat:{category_name}.{subcategory_name or str()}'

        search = Search(
            query=query,
            max_results=limit,
            sort_by=SortCriterion.SubmittedDate,
            sort_order=SortOrder.Descending,
        )
        client = Client()

        results = [result for result in client.results(search)]
        # TODO map to MathArticle

        return results

    def get_category_name(category: BaseCategory) -> str:
        if type[category] == PhysCategory:
            return category.name.lower()

        return CATEGORY_TYPE_TO_PREFIX[type[category]]

    def get_subcategory_name(category: BaseCategory) -> str | None:
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
