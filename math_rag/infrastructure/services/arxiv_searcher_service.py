from arxiv import Client, Result, Search, SortCriterion, SortOrder

from math_rag.core.base import BaseCategory


class ArxivSearcherService:
    def search(self, category: BaseCategory, limit: int) -> list[Result]:
        search = Search(
            query=...,  # 'cat:math.PR'
            max_results=limit,
            sort_by=SortCriterion.SubmittedDate,
            sort_order=SortOrder.Descending,
        )
        client = Client()

        results = [result for result in client.results(search)]

        return results
