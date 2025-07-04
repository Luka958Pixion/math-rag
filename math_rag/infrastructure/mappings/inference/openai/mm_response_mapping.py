from math_rag.application.models.inference import MMCategory, MMResponse
from math_rag.infrastructure.base import BaseMapping
from openai.types import Moderation


class MMResponseMapping(BaseMapping[MMResponse, Moderation]):
    @staticmethod
    def to_source(target: Moderation) -> MMResponse:
        return MMResponse(
            categories=[
                MMCategory(name=field, is_flagged=value)
                for field, value in target.categories.model_dump().items()
            ]
        )

    @staticmethod
    def to_target(source: MMResponse) -> Moderation:
        raise NotImplementedError()
