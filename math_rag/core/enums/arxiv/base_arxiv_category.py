from enum import Enum


class BaseArxivCategory(str, Enum):
    @classmethod
    def from_str(cls, category_str: str) -> 'BaseArxivCategory':
        try:
            return cls[category_str.upper()]

        except KeyError:
            raise ValueError(f'Category {category_str} not found in {cls.__name__}')
