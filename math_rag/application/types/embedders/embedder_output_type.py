from typing import TypeVar

from math_rag.application.models.embedders.base import BaseEmbedderOutput


EmbedderOutputType = TypeVar('EmbedderOutputType', bound=BaseEmbedderOutput)
