from typing import TypeVar

from math_rag.application.models.moderators.base import BaseModeratorOutput


ModeratorOutputType = TypeVar('ModeratorOutputType', bound=BaseModeratorOutput)
