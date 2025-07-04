from typing import Callable, Iterable, TypeAlias, TypeVar
from uuid import UUID

from pydantic import BaseModel

from math_rag.application.types.assistants import AssistantInputType
from math_rag.application.types.embedders import EmbedderInputType
from math_rag.application.types.moderators import ModeratorInputType


T = TypeVar('T', bound=BaseModel)
R: TypeAlias = AssistantInputType | EmbedderInputType | ModeratorInputType


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
