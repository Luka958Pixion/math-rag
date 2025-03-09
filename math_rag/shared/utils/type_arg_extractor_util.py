from typing import TypeVar, get_args


GenericType = TypeVar('TypeGeneric')


class TypeArgExtractorUtil:
    @staticmethod
    def extract(cls: type[GenericType]) -> dict[int, type | tuple[type, ...]]:
        args: dict[int, type | tuple[type, ...]] = {
            i: get_args(base)[0] if len(get_args(base)) == 1 else get_args(base)
            for i, base in enumerate(cls.__orig_bases__)
        }

        if not args:
            raise TypeError(f'No generic base classes found in {cls.__orig_bases__}')

        return args
