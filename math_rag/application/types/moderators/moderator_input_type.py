from typing import TypeVar

from math_rag.application.models.moderators.base import BaseModeratorInput


ModeratorInputType = TypeVar('ModeratorInputType', bound=BaseModeratorInput)
