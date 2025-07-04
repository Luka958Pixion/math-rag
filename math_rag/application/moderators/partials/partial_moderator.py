from math_rag.application.base.inference import BaseManagedEM
from math_rag.application.types.moderators import ModeratorInputType, ModeratorOutputType

from .partial_basic_moderator import PartialBasicModerator
from .partial_concurrent_moderator import PartialConcurrentModerator


class PartialModerator(
    PartialBasicModerator[ModeratorInputType, ModeratorOutputType],
    PartialConcurrentModerator[ModeratorInputType, ModeratorOutputType],
):
    def __init__(self, em: BaseManagedEM):
        PartialBasicModerator.__init__(self, em)
        PartialConcurrentModerator.__init__(self, em)
