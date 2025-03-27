from enum import Enum


class PBSProJobState(str, Enum):
    """
    PBS Pro 2022.1.1 Job States

    Reference:
        https://help.altair.com/2022.1.0/PBS%20Professional/PBSReferenceGuide2022.1.pdf
    """

    B = 'begun'
    """(7): Job arrays only; at least one subjob has started."""

    E = 'exiting'
    """(5): Job is exiting after having run."""

    F = 'finished'
    """(9): Job has completed execution, failed during execution, or was deleted."""

    H = 'held'
    """(2): Job is held by user, admin, or server."""

    M = 'moved'
    """(8): Job was moved to another server."""

    Q = 'queued'
    """(1): Job is queued, eligible to run or be routed."""

    R = 'running'
    """(4): Job is currently running."""

    S = 'suspended'
    """(400): Job is suspended by scheduler to free up resources."""

    T = 'transition'
    """(0): Job is transitioning to or from a server."""

    U = 'unknown'
    """(410): Job is suspended due to workstation becoming busy."""

    W = 'waiting'
    """(3): Job is waiting for its execution time or delayed due to stagein failure."""

    X = 'exited'
    """(6): Subjobs only; subjob is finished or expired."""
