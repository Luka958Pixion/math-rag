import asyncio
import atexit
import logging
import os
import sys

from collections.abc import Awaitable, Callable
from typing import Any

import nest_asyncio

from IPython.core.interactiveshell import InteractiveShell


class NotebookHook:
    def __init__(self, ip: InteractiveShell, reset: bool = True) -> None:
        self.ip = ip
        self.reset = reset
        self._cleanup: list[Callable[[], None]] = []
        self._async_cleanup: list[Callable[[], Awaitable[None]]] = []

        atexit.register(self._run_cleanup)

        self._apply_startup()
        self._init_containers()

    def _apply_startup(self) -> None:
        # magics
        self.ip.run_line_magic('load_ext', 'autoreload')
        self.ip.run_line_magic('autoreload', '2')

        # patch path
        hook_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(hook_dir, '..', '..'))
        sys.path.insert(0, project_root)

        # patch asyncio
        nest_asyncio.apply()

        # logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
        logging.getLogger('pylatexenc.latexwalker').setLevel(logging.ERROR)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('openai').setLevel(logging.WARNING)
        logging.getLogger('asyncssh').setLevel(logging.WARNING)

    def _init_containers(self) -> None:
        # import after path adjustment
        from math_rag.infrastructure.containers import InfrastructureContainer

        # initialize DI containers
        self.infrastructure_container: InfrastructureContainer = InfrastructureContainer()
        self.infrastructure_container.init_resources()
        self.infrastructure_container.wire(modules=[__name__])

        self.application_container = self.infrastructure_container.application_container()
        self.application_container.init_resources()
        self.application_container.wire(modules=[__name__])

        # inject container into user namespace
        self.ip.user_ns['infrastructure_container'] = self.infrastructure_container
        self.ip.user_ns['application_container'] = self.application_container

        # run sync seeders
        for seeder in self.infrastructure_container.object_seeders():
            seeder.seed(reset=self.reset)

        # run async seeders and indexers
        async def _async_tasks() -> None:
            for seeder in self.infrastructure_container.document_seeders():
                await seeder.seed(reset=self.reset)
            for seeder in self.infrastructure_container.embedding_seeders():
                await seeder.seed(reset=self.reset)
            for indexer in self.infrastructure_container.document_indexers():
                await indexer.index(reset=self.reset)

        # execute async tasks via event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_async_tasks())

    def add_cleanup(self, func: Callable[..., Any], *, async_: bool = False) -> None:
        if async_:
            self._async_cleanup.append(func)
        else:
            self._cleanup.append(func)

    def _run_cleanup(self) -> None:
        # sync cleanup tasks
        for cb in self._cleanup:
            try:
                cb()
            except Exception as e:
                print(f'Error in cleanup callback {cb!r}: {e}')

        # async cleanup tasks via same loop
        loop = asyncio.get_event_loop()
        for coro in self._async_cleanup:
            try:
                loop.run_until_complete(coro())

            except Exception as e:
                print(f'Error in async cleanup {coro!r}: {e}')


def load_ipython_extension(ipython: InteractiveShell) -> None:
    """
    Loads the NotebookHook, reading RESET from user namespace.

    Usage:
    ```
    RESET = False
    %load_ext hooks.notebook_hook
    ```
    """
    reset_flag = ipython.user_ns.get('RESET', True)
    hook = NotebookHook(ipython, reset_flag)
    setattr(ipython, 'nb_hook', hook)
