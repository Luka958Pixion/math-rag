from abc import ABC, abstractmethod

from math_rag.application.models.clients import (
    JupyterEndSessionResult,
    JupyterExecuteCodeResult,
    JupyterResetSessionResult,
    JupyterStartSessionResult,
)


class BaseJupyterClient(ABC):
    @abstractmethod
    async def start_session(self, user_id: str) -> JupyterStartSessionResult:
        pass

    @abstractmethod
    async def execute_code(self, user_id: str, code: str) -> JupyterExecuteCodeResult:
        pass

    @abstractmethod
    async def reset_session(self, user_id: str) -> JupyterResetSessionResult:
        pass

    @abstractmethod
    async def end_session(self, user_id: str) -> JupyterEndSessionResult:
        pass

    @abstractmethod
    async def health(self) -> bool:
        pass
