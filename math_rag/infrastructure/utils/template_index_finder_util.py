import re

from math_rag.infrastructure.constants.services import MATH_PLACEHOLDER_INDEX_PATTERN


class TemplateIndexFinderUtil:
    @staticmethod
    def find(text: str) -> list[int]:
        matches = re.finditer(MATH_PLACEHOLDER_INDEX_PATTERN, text)
        indexes = []

        for match in matches:
            index = match.group(1)

            if index is None:
                raise ValueError(f'Match "{match}" does not have an index')

            indexes.append(int(index))

        return indexes
