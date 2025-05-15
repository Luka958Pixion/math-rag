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
        super().__init__(client)
