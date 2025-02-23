from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import DocumentBaseRepository


class MongoDocumentRepository(DocumentBaseRepository):
    def __init__(self, host: str, deployment: str):
        self.client = AsyncMongoClient(host, uuidRepresentation='standard')
        self.db = self.client[deployment]

    async def create_collection(self, name: str):
        collection_names = await self.db.list_collection_names()

        if name in collection_names:
            return self.db[name]

        return self.db.create_collection(name)

    async def delete_collection(self, name: str):
        collection_names = await self.db.list_collection_names()

        if name in collection_names:
            return self.db[name].drop()

    async def insert_documents(self, collection_name: str, documents: list[dict]):
        for document in documents:
            document['_id'] = document.pop('id')

        await self.db[collection_name].insert_many(documents)
