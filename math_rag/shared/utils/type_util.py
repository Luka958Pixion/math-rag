from importlib import import_module
from inspect import getfile
from pathlib import Path
from types import UnionType
from typing import Generic, TypeVar, Union, get_args, get_origin


T = TypeVar('T')


class TypeUtil(Generic[T]):
    @staticmethod
    def get_type_args(cls: type[T]) -> dict[int, type | tuple[type, ...]]:
        args: dict[int, type | tuple[type, ...]] = {
            i: get_args(base)[0] if len(get_args(base)) == 1 else get_args(base)
            for i, base in enumerate(cls.__orig_bases__)
        }

        if not args:
            raise TypeError(f'No generic base classes found in {cls.__orig_bases__}')

        return args

    @staticmethod
    def to_fqn(type: type[T]) -> str:
        module_parts = type.__module__.split('.')

        if len(module_parts) > 1:
            module_parts.pop()

        module = '.'.join(module_parts)

        return f'{module}.{type.__qualname__}'

    @staticmethod
    def from_fqn(fqn: str) -> type[T]:
        module_name, class_name = fqn.rsplit('.', 1)
        module = import_module(module_name)
        type = getattr(module, class_name)

        return type

    @staticmethod
    def extract_optional_type(annotation: type[T] | None) -> type[T]:
        origin = get_origin(annotation)

        if origin in (Union, UnionType):
            args = get_args(annotation)

            if len(args) == 2 and any(arg is type(None) for arg in args):
                return args[0] if args[1] is type(None) else args[1]

        return annotation

    @staticmethod
    def get_file_name(cls: type) -> str:
        return Path(getfile(cls)).stem
