from math_rag.infrastructure.services.arxiv import BaseArxivCategory


class QuantBioCategory(BaseArxivCategory):
    BM = 'biomolecules'
    CB = 'cell_behavior'
    GN = 'genomics'
    MN = 'molecular_networks'
    NC = 'neurons_and_cognition'
    OT = 'other_quantitative_biology'
    PE = 'populations_and_evolution'
    QM = 'quantitative_methods'
    SC = 'subcellular_processes'
    TO = 'tissues_and_organs'
