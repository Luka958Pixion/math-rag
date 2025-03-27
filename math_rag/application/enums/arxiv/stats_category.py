from math_rag.infrastructure.services.arxiv import BaseArxivCategory


class StatsCategory(BaseArxivCategory):
    AP = 'applications'
    CO = 'computation'
    ME = 'methodology'
    ML = 'machine_learning'
    OT = 'other_statistics'
    TH = 'statistics_theory'
