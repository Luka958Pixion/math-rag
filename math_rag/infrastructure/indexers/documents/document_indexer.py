from typing import Generic, cast

from pymongo import ASCENDING, AsyncMongoClient
from pymongo.operations import IndexModel

from math_rag.application.base.indexers.documents import BaseDocumentIndexer
from math_rag.infrastructure.types.repositories.documents import TargetType
from math_rag.shared.utils import StrUtil, TypeUtil


class DocumentIndexer(BaseDocumentIndexer, Generic[TargetType]):
    def __init__(self, client: AsyncMongoClient, deployment: str, fields: list[str]):
        args = TypeUtil.get_type_args(self.__class__)
        self.target_cls = cast(type[TargetType], args[0])

        self.client = client
        self.db = self.client[deployment]
        self.collection_name = StrUtil.to_snake_case(self.target_cls.__name__)
        self.collection = self.db[self.collection_name]
        self.fields = fields

    async def index(self, reset: bool = False):
        if reset:
            indexes = await self.collection.index_information()

            for name, _ in indexes.items():
                if name != '_id_':
                    await self.collection.drop_index(name)

        index_models = []

        for field in self.fields:
            if field not in self.target_cls.model_fields:
                raise ValueError(f'Document {self.target_cls.__name__} does not have field {field}')

            index_model = IndexModel([(field, ASCENDING)], background=False)
            index_models.append(index_model)

        await self.collection.create_indexes(index_models)
