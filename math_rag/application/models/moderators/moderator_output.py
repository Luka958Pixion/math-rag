from math_rag.application.models.moderators.base import BaseModeratorOutput


class ModeratorOutput(BaseModeratorOutput):
    is_flagged: bool
