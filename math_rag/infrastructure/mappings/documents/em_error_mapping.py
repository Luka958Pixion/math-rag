from math_rag.application.models.inference import EMError
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import EMErrorDocument


class EMErrorMapping(BaseMapping[EMError, EMErrorDocument]):
    @staticmethod
    def to_source(target: EMErrorDocument) -> EMError:
        return EMError(id=target.id, message=target.message, body=target.body)

    @staticmethod
    def to_target(source: EMError) -> EMErrorDocument:
        return EMErrorDocument(id=source.id, message=source.message, body=source.body)
