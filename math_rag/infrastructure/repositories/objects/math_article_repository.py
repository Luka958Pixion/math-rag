from pathlib import Path

from minio import Minio

from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.core.models import MathArticle
from math_rag.infrastructure.mappings.objects import MathArticleMapping
from math_rag.infrastructure.models.objects import MathArticleObject

from .object_repository import ObjectRepository


BACKUP_PATH = Path('../../../../.tmp/backups/minio')


class MathArticleRepository(
    BaseMathArticleRepository,
    ObjectRepository[MathArticle, MathArticleObject, MathArticleMapping],
):
    def __init__(self, client: Minio):
        metadata_keys = ['id', 'timestamp']

        for key in metadata_keys:
            if key not in MathArticleObject.model_fields:
                raise ValueError(
                    f'Field {key} does not exist in {MathArticleObject.__class__.__name__}'
                )

        super().__init__(client, metadata_keys)
