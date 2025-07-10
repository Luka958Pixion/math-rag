from typing import Callable, Iterable, TypeVar
from uuid import UUID

from pydantic import BaseModel

from math_rag.application.models.assistants.base import BaseAssistantInput
from math_rag.application.models.embedders.base import BaseEmbedderInput
from math_rag.application.models.moderators.base import BaseModeratorInput


T = TypeVar('T', bound=BaseModel)
R = TypeVar('R', bound=BaseAssistantInput | BaseEmbedderInput | BaseModeratorInput)


class InputCreatorUtil:
    @staticmethod
    def create(
        items: Iterable[T],
        callback: Callable[[T], R],
    ) -> tuple[list[R], dict[UUID, T]]:
        inputs: list[R] = []
        input_id_to_item: dict[UUID, T] = {}

        for item in items:
            input = callback(item)
            inputs.append(input)
            input_id_to_item[input.id] = item

        return inputs, input_id_to_item
