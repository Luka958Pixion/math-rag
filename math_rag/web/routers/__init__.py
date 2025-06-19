import importlib
import pkgutil

from fastapi import APIRouter


routers: list[APIRouter] = []

for _, module_name, _ in pkgutil.walk_packages(__path__, prefix=__name__ + '.'):
    module = importlib.import_module(module_name)
    router = getattr(module, 'router', None)

    if router:
        routers.append(router)

__all__ = ['routers']
