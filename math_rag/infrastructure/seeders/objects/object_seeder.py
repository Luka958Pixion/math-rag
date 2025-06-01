from typing import Generic, cast

from minio import Minio

from math_rag.application.base.seeders.objects import BaseObjectSeeder
from math_rag.infrastructure.types.repositories.objects import TargetType
from math_rag.shared.utils import TypeUtil


class ObjectSeeder(BaseObjectSeeder, Generic[TargetType]):
    def __init__(self, client: Minio):
        args = TypeUtil.get_type_args(self.__class__)
        self.target_cls = cast(type[TargetType], args[0])

        self.client = client
        self.bucket_name = self.target_cls.__name__.lower()

    def seed(self, reset=False):
        if reset:
            self._delete_bucket()

        self._create_bucket()

    def _create_bucket(self):
        if self.client.bucket_exists(self.bucket_name):
            return

        self.client.make_bucket(self.bucket_name)

    def _delete_bucket(self):
        if not self.client.bucket_exists(self.bucket_name):
            return

        objects = list(self.client.list_objects(self.bucket_name, recursive=True))

        for object in objects:
            self.client.remove_object(self.bucket_name, object.object_name)

        self.client.remove_bucket(self.bucket_name)
