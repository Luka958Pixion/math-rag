from typing import TypeVar

from math_rag.application.models.embedants.base import BaseEmbedantOutput


EmbedantOutputType = TypeVar('EmbedantOutputType', bound=BaseEmbedantOutput)
