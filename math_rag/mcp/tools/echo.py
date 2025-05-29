from dependency_injector.wiring import Provide, inject

from math_rag.application.containers import ApplicationContainer


def echo_tool():
    print('hello world')
