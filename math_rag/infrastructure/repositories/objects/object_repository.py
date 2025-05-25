from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Generic, cast

from minio import Minio

from math_rag.application.base.repositories.objects import BaseObjectRepository
from math_rag.infrastructure.types.repositories.objects import (
    MappingType,
    SourceType,
    TargetType,
)
from math_rag.shared.utils import TypeUtil


BACKUP_PATH = Path(__file__).parents[4] / '.tmp' / 'backups' / 'minio'


class ObjectRepository(
    BaseObjectRepository[SourceType], Generic[SourceType, TargetType, MappingType]
):
    def __init__(self, client: Minio):
        args = TypeUtil.get_type_args(self.__class__)
        self.source_cls = cast(type[SourceType], args[1][0])
        self.target_cls = cast(type[TargetType], args[1][1])
        self.mapping_cls = cast(type[MappingType], args[1][2])

        self.client = client
        self.bucket_name = self.target_cls.__name__.lower()

    def insert_one(self, item: SourceType):
        object = self.mapping_cls.to_target(item)
        # NOTE: can't use unpacking because data is not serializable
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object.object_name,
            data=object.data,
            length=object.length,
            content_type=object.content_type,
            metadata=object.metadata,
            sse=object.sse,
            progress=object.progress,
            part_size=object.part_size,
            num_parallel_uploads=object.num_parallel_uploads,
            tags=object.tags,
            retention=object.retention,
            legal_hold=object.legal_hold,
        )

    def insert_many(self, items: list[SourceType]):
        objects = [self.mapping_cls.to_target(item) for item in items]

        for object in objects:
            # NOTE: can't use unpacking because data is not serializable
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object.object_name,
                data=object.data,
                length=object.length,
                content_type=object.content_type,
                metadata=object.metadata,
                sse=object.sse,
                progress=object.progress,
                part_size=object.part_size,
                num_parallel_uploads=object.num_parallel_uploads,
                tags=object.tags,
                retention=object.retention,
                legal_hold=object.legal_hold,
            )

    def find_by_name(self, name: str) -> SourceType:
        object_response = self.client.get_object(self.bucket_name, name)
        object_bytes = BytesIO(object_response.read())
        object_response.close()
        object_response.release_conn()

        stat_response = self.client.stat_object(self.bucket_name, name)
        id = stat_response.metadata.get('X-Amz-Meta-id')
        index_id = stat_response.metadata.get('X-Amz-Meta-index-id')
        timestamp = stat_response.metadata.get('X-Amz-Meta-timestamp')

        if id is None:
            raise ValueError(f'Missing X-Amz-Meta-id in {name}')

        if index_id is None:
            raise ValueError(f'Missing X-Amz-Meta-index-id in {name}')

        if timestamp is None:
            raise ValueError(f'Missing X-Amz-Meta-timestamp in {name}')

        object = self.target_cls(
            object_name=name,
            data=object_bytes,
            length=object_bytes.getbuffer().nbytes,
            metadata={
                'X-Amz-Meta-id': id,
                'X-Amz-Meta-index-id': index_id,
                'X-Amz-Meta-timestamp': timestamp,
            },
        )
        item = self.mapping_cls.to_source(object)

        return item

    def list_names(self) -> list[str | None]:
        objects = self.client.list_objects(self.bucket_name, recursive=True)

        return [object.object_name for object in objects]

    def clear(self):
        objects = self.client.list_objects(self.bucket_name, recursive=True)

        for object in objects:
            self.client.remove_object(self.bucket_name, object.object_name)

    def backup(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.backup_dir_path = BACKUP_PATH / timestamp / self.bucket_name
        self.backup_dir_path.mkdir(parents=True, exist_ok=True)

        for object_name in self.list_names():
            local_path = self.backup_dir_path / object_name
            local_path.parent.mkdir(parents=True, exist_ok=True)
            self.client.fget_object(self.bucket_name, object_name, str(local_path))

    def restore(self):
        self.clear()

        for path in self.backup_dir_path.rglob('*'):
            if path.is_file():
                object_name = str(path.relative_to(self.backup_dir_path))
                self.client.fput_object(self.bucket_name, object_name, str(path))
