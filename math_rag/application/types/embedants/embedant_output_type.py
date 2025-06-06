from typing import TypeVar

from math_rag.application.base.embedants import BaseEmbedantOutput


EmbedantOutputType = TypeVar('EmbedantOutputType', bound=BaseEmbedantOutput)
