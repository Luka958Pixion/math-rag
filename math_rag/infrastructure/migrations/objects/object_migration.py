from typing import Generic, cast
from uuid import UUID

from minio import Minio

from math_rag.infrastructure.types.repositories.objects import TargetType
from math_rag.shared.utils import TypeUtil


class ObjectMigration(Generic[TargetType]):
    def __init__(self, client: Minio):
        args = TypeUtil.get_type_args(self.__class__)
        self.target_cls = cast(type[TargetType], args[1][0])

        self.client = client
        self.bucket_name = self.target_cls.__name__.lower()

    def add_field(self, field: str, id_to_field_value: dict[UUID, str]) -> None:
        for object in self.client.list_objects(self.bucket_name, recursive=True):
            stat = self.client.stat_object(self.bucket_name, object.object_name)
            metadata = stat.metadata or {}
            id = metadata.get('X-Amz-Meta-id')

            if not id:
                raise ValueError(f'Object {object.object_name} does not have an id')

            if id not in id_to_field_value:
                continue

            metadata[field] = id_to_field_value[id]

            self.client.copy_object(
                bucket_name=self.bucket_name,
                object_name=object.object_name,
                source=f'/{self.bucket_name}/{object.object_name}',
                metadata=metadata,
                metadata_directive='REPLACE',
            )

    def remove_field(self, field: str) -> None:
        for object in self.client.list_objects(self.bucket_name, recursive=True):
            stat = self.client.stat_object(self.bucket_name, object.object_name)
            metadata = stat.metadata or {}

            if field in metadata:
                metadata.pop(field)

                self.client.copy_object(
                    bucket_name=self.bucket_name,
                    object_name=object.object_name,
                    source=f'/{self.bucket_name}/{object.object_name}',
                    metadata=metadata,
                    metadata_directive='REPLACE',
                )
