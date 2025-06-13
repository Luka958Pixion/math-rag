from typing import TypeAlias

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


ArxivCategoryType: TypeAlias = (
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
