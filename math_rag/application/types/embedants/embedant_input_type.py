from typing import TypeVar

from math_rag.application.base.embedants import BaseEmbedantInput


EmbedantInputType = TypeVar('EmbedantInputType', bound=BaseEmbedantInput)
