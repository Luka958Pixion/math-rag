from pymongo import AsyncMongoClient

from math_rag.core.base import ObjectBaseRepository


class MongoObjectRepository(ObjectBaseRepository):
    def __init__(self, host: str, deployment: str):
        self.client = AsyncMongoClient(host)
        self.db = self.client[deployment]

    async def create_collection(self, name: str):
        if name in self.db.list_collection_names():
            return self.db[name]

        return self.db.create_collection(name)

    async def delete_collection(self, name: str):
        if name in self.db.list_collection_names():
            return self.db[name].drop()
