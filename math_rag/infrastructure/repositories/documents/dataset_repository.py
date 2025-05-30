from typing import Generic
from uuid import UUID

from pymongo import AsyncMongoClient, ReturnDocument

from math_rag.application.base.repositories.documents import BaseDatasetRepository
from math_rag.core.enums import DatasetBuildStatus
from math_rag.core.types import DatasetBuildStageType, SampleType
from math_rag.infrastructure.types.repositories.documents import (
    MappingType,
    SourceType,
    TargetType,
)

from .document_repository import DocumentRepository


class DatasetRepository(
    BaseDatasetRepository[SampleType, DatasetBuildStageType],
    DocumentRepository[SourceType, TargetType, MappingType],
    Generic[SampleType, DatasetBuildStageType, SourceType, TargetType, MappingType],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)

    async def update_build_stage(self, id: UUID, build_stage: DatasetBuildStageType) -> SourceType:
        field = 'build_stage'

        if field not in self.target_cls.model_fields:
            raise ValueError(f'{self.target_cls.__name__} does not have field {field}')

        bson_doc = await self.collection.find_one_and_update(
            filter={'_id': id},
            update={'$set': {field: build_stage.value}},
            return_document=ReturnDocument.AFTER,
        )
        doc = self.target_cls.model_validate(bson_doc)

        return self.mapping_cls.to_source(doc)

    async def update_build_status(self, id: UUID, build_status: DatasetBuildStatus) -> SourceType:
        field = 'build_status'

        if field not in self.target_cls.model_fields:
            raise ValueError(f'{self.target_cls.__name__} does not have field {field}')

        bson_doc = await self.collection.find_one_and_update(
            filter={'_id': id},
            update={'$set': {field: build_status.value}},
            return_document=ReturnDocument.AFTER,
        )
        doc = self.target_cls.model_validate(bson_doc)

        return self.mapping_cls.to_source(doc)

    async def find_first_pending(self) -> SourceType | None:
        bson_doc = await self.collection.find_one(
            filter={'build_status': DatasetBuildStatus.PENDING.value},
            sort=[('timestamp', 1)],
        )

        if bson_doc is None:
            return None

        doc = self.target_cls.model_validate(bson_doc)

        return self.mapping_cls.to_source(doc)
