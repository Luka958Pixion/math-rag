from enum import Enum


class PBSProJobState(str, Enum):
    """
    PBS Pro 2024.1.0 Job States

    Reference:
        https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf
    """

    BEGUN = 'B'
    """Job array has started execution."""

    EXITING = 'E'
    """The Exiting state."""

    FINISHED = 'F'
    """The Finished state."""

    HELD = 'H'
    """The Held state."""

    MOVED = 'M'
    """The Moved state."""

    QUEUED = 'Q'
    """The Queued state."""

    RUNNING = 'R'
    """The Running state."""

    SUSPENDED = 'S'
    """The Suspended state."""

    TRANSITING = 'T'
    """The Transiting state."""

    USER_SUSPENDED = 'U'
    """Job suspended due to workstation user activity."""

    WAITING = 'W'
    """The Waiting state."""

    EXITED = 'X'
    """The Exited state (subjobs only)."""
