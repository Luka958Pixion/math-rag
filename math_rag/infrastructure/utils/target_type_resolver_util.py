import functools
import importlib
import inspect
import pkgutil

from math_rag.infrastructure.base import BaseMapping
from math_rag.shared.utils import TypeUtil


MODULE_NAME = 'math_rag.infrastructure.mappings'


class TargetTypeResolverUtil:
    @staticmethod
    @functools.lru_cache
    def _type_cache(module_name: str) -> dict[type, type]:
        module = importlib.import_module(module_name)
        mapping: dict[type, type] = {}

        for _, module_name, _ in pkgutil.walk_packages(module.__path__, module.__name__ + '.'):
            mod = importlib.import_module(module_name)

            for _, cls in inspect.getmembers(mod, inspect.isclass):
                if (
                    cls is not BaseMapping
                    and issubclass(cls, BaseMapping)
                    and not inspect.isabstract(cls)
                ):
                    source_cls, target_cls = TypeUtil.get_type_args(cls)[0]
                    mapping[source_cls] = target_cls

        return mapping

    @staticmethod
    def resolve(*, source_cls: type) -> type:
        return TargetTypeResolverUtil._type_cache(MODULE_NAME)[source_cls]
