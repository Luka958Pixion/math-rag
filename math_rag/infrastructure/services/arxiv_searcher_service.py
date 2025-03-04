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
from math_rag.core.enums.categories.physics import (
    AstroPhPhysSubCategory,
    CondMatPhysSubCategory,
    NlinPhysSubCategory,
    PhysicsPhysSubCategory,
)


class ArxivSearcherService:
    def search(self, category: BaseCategory, limit: int) -> list[Result]:
        PHYSICS = {
            AstroPhPhysSubCategory: 'astro-ph',
            CondMatPhysSubCategory: 'cond-mat',
            NlinPhysSubCategory: 'nlin',
            PhysicsPhysSubCategory: 'physics',
        }
        CATEGORY_PREFIXES = {
            CompSciCategory: 'cs',
            EconCategory: 'econ',
            EESSCategory: 'eess',
            MathCategory: 'math',
            PhysCategory: ...,  # TODO use PHYSICS
            QuantBioCategory: 'q-bio',
            QuantFinCategory: 'q-fin',
            StatsCategory: 'stat',
        }

        search = Search(
            query=...,  # 'cat:math.PR'
            max_results=limit,
            sort_by=SortCriterion.SubmittedDate,
            sort_order=SortOrder.Descending,
        )
        client = Client()

        results = [result for result in client.results(search)]

        return results
