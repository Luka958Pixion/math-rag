from math_rag.infrastructure.services.arxiv import BaseArxivCategory


class QuantFinCategory(BaseArxivCategory):
    CP = 'computational_finance'
    EC = 'economics'
    GN = 'general_finance'
    MF = 'mathematical_finance'
    PM = 'portfolio_management'
    PR = 'pricing_of_securities'
    RM = 'risk_management'
    ST = 'statistical_finance'
    TR = 'trading_and_market_microstructure'
