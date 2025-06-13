from enum import Enum

from math_rag.core.enums.arxiv import (
    CompSciCategory,
    EconCategory,
    EESSCategory,
    MathCategory,
    PhysCategory,
    QuantBioCategory,
    QuantFinCategory,
    StatsCategory,
)
from math_rag.core.enums.arxiv.physics import (
    AstroPhCategory,
    CondMatCategory,
    NlinCategory,
    PhysicsCategory,
)


class ArxivCategoryType(str, Enum):
    CompSciCategory = CompSciCategory.__name__
    EconCategory = EconCategory.__name__
    EESSCategory = EESSCategory.__name__
    MathCategory = MathCategory.__name__
    PhysCategory = PhysCategory.__name__
    QuantBioCategory = QuantBioCategory.__name__
    QuantFinCategory = QuantFinCategory.__name__
    StatsCategory = StatsCategory.__name__
    AstroPhCategory = AstroPhCategory.__name__
    CondMatCategory = CondMatCategory.__name__
    NlinCategory = NlinCategory.__name__
    PhysicsCategory = PhysicsCategory.__name__


ArxivCategory = (
    CompSciCategory
    | EconCategory
    | EESSCategory
    | MathCategory
    | PhysCategory
    | QuantBioCategory
    | QuantFinCategory
    | StatsCategory
    | AstroPhCategory
    | CondMatCategory
    | NlinCategory
    | PhysicsCategory
)
