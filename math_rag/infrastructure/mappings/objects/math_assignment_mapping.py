from datetime import datetime
from io import BytesIO
from uuid import UUID

from math_rag.core.models import MathAssignment
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.objects import MathAssignmentObject


class MathAssignmentMapping(BaseMapping[MathAssignment, MathAssignmentObject]):
    @staticmethod
    def to_source(target: MathAssignmentObject) -> MathAssignment:
        id = target.metadata.get('X-Amz-Meta-id')
        timestamp = target.metadata.get('X-Amz-Meta-timestamp')

        if id is None:
            raise ValueError(f'Missing X-Amz-Meta-id in {target.object_name}')

        if timestamp is None:
            raise ValueError(f'Missing X-Amz-Meta-timestamp in {target.object_name}')

        return MathAssignment(
            id=UUID(id),
            timestamp=datetime.fromisoformat(timestamp),
            name=target.object_name,
            bytes=target.data.read(),
        )

    @staticmethod
    def to_target(source: MathAssignment) -> MathAssignmentObject:
        data = BytesIO(source.bytes)

        return MathAssignmentObject(
            object_name=source.name,
            data=data,
            length=data.getbuffer().nbytes,
            metadata={
                'X-Amz-Meta-id': str(source.id),
                'X-Amz-Meta-timestamp': source.timestamp.isoformat(),
            },
        )
