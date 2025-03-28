from enum import Enum


class PBSProJobState(str, Enum):
    """
    PBS Pro 2022.1.1 Job States

    Reference:
        https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf
    """

    BEGUN = 'B'
    """(7): Job arrays only; at least one subjob has started."""

    EXITING = 'E'
    """(5): Job is exiting after having run."""

    FINISHED = 'F'
    """(9): Job has completed execution, failed during execution, or was deleted."""

    HELD = 'H'
    """(2): Job is held by user, admin, or server."""

    MOVED = 'M'
    """(8): Job was moved to another server."""

    QUEUED = 'Q'
    """(1): Job is queued, eligible to run or be routed."""

    RUNNING = 'R'
    """(4): Job is currently running."""

    SUSPENDED = 'S'
    """(400): Job is suspended by scheduler to free up resources."""

    TRANSITION = 'T'
    """(0): Job is transitioning to or from a server."""

    UNKNOWN = 'U'
    """(410): Job is suspended due to workstation becoming busy."""

    WAITING = 'W'
    """(3): Job is waiting for its execution time or delayed due to stagein failure."""

    EXITED = 'X'
    """(6): Subjobs only; subjob is finished or expired."""
