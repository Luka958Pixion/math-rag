from typing import TypeVar

from math_rag.application.models.embedders.base import BaseEmbedderInput


EmbedderInputType = TypeVar('EmbedderInputType', bound=BaseEmbedderInput)
