from abc import ABC, abstractmethod


class DocumentBaseRepository(ABC):
    @abstractmethod
    async def create_collection(self, name: str):
        pass

    @abstractmethod
    async def delete_collection(self, name: str):
        pass
