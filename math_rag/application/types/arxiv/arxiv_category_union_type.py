import inspect

from enum import Enum
from typing import Union

import math_rag.application.enums.arxiv as arxiv_categories_module
import math_rag.application.enums.arxiv.physics as arxiv_physics_categories_module

from math_rag.application.enums.arxiv import BaseArxivCategory


# arxiv_category_type: type[ArxivCategoryType] | None,
# arxiv_category: ArxivCategoryType | None,
modules = [arxiv_categories_module, arxiv_physics_categories_module]

_all_arxiv_category_enums_dict = {
    name: member
    for module in modules
    for name, member in inspect.getmembers(module)
    if inspect.isclass(member)
    and issubclass(member, BaseArxivCategory)
    and member is not BaseArxivCategory
}

ArxivCategoryUnionType = Union[tuple(_all_arxiv_category_enums_dict.values())]
ArxivCategoryUnionTypeEnum = Enum(
    'ArxivCategoryUnionTypeEnum', {name: name for name in _all_arxiv_category_enums_dict}
)
