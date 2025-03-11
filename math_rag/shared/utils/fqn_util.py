from typing import TypeVar


T = TypeVar('T')


class FQNUtil:
    @staticmethod
    def get_fqn(type: type[T]) -> str:
        return f'{type.__module__}.{type.__qualname__}'
