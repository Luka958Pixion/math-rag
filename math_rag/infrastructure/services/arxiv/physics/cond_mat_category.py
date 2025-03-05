from math_rag.infrastructure.services.arxiv import BaseArxivCategory


class CondMatCategory(BaseArxivCategory):
    DIS_NN = 'disordered_systems_and_neural_networks'
    MES_HALL = 'mesoscale_and_nanoscale_physics'
    MTRL_SCI = 'materials_science'
    OTHER = 'other_condensed_matter'
    QUANT_GAS = 'quantum_gases'
    SOFT = 'soft_condensed_matter'
    STAT_MECH = 'statistical_mechanics'
    STR_EL = 'strongly_correlated_electrons'
    SUPR_CON = 'superconductivity'
