from typing import TypeVar

from math_rag.application.models.embedants.base import BaseEmbedantInput


EmbedantInputType = TypeVar('EmbedantInputType', bound=BaseEmbedantInput)
