from datetime import datetime
from io import BytesIO
from uuid import UUID

from math_rag.core.models import MathArticle
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.objects import MathArticleObject


class MathArticleMapping(BaseMapping[MathArticle, MathArticleObject]):
    @staticmethod
    def to_source(target: MathArticleObject) -> MathArticle:
        id = target.metadata.get('X-Amz-Meta-id')
        dataset_id = target.metadata.get('X-Amz-Meta-dataset_id')
        index_id = target.metadata.get('X-Amz-Meta-index_id')
        timestamp = target.metadata.get('X-Amz-Meta-timestamp')

        if id is None:
            raise ValueError(f'Missing X-Amz-Meta-id in {target.object_name}')

        if timestamp is None:
            raise ValueError(f'Missing X-Amz-Meta-timestamp in {target.object_name}')

        return MathArticle(
            id=UUID(id),
            dataset_id=dataset_id,
            index_id=index_id,
            timestamp=datetime.fromisoformat(timestamp),
            name=target.object_name,
            bytes=target.data.read(),
        )

    @staticmethod
    def to_target(source: MathArticle) -> MathArticleObject:
        data = BytesIO(source.bytes)

        return MathArticleObject(
            object_name=source.name,
            data=data,
            length=data.getbuffer().nbytes,
            metadata={
                'X-Amz-Meta-id': str(source.id),
                'X-Amz-Meta-dataset_id': str(source.dataset_id),
                'X-Amz-Meta-index_id': str(source.index_id),
                'X-Amz-Meta-timestamp': source.timestamp.isoformat(),
            },
        )
