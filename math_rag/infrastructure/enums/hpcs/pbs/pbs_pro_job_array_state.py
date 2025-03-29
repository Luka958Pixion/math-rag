from enum import Enum


class PBSProJobArrayState(str, Enum):
    """
    PBS Pro 2022.1.1 Job Array States

    Reference:
        https://help.altair.com/2022.1.0/PBS%20Professional/PBSReferenceGuide2022.1.pdf
    """

    B = 'begun'
    """Job array has begun; at least one subjob has started execution."""

    E = 'exiting'
    """Job is exiting after having run."""

    F = 'finished'
    """Job has finished execution; it has either completed successfully, failed during execution, or was deleted."""

    H = 'held'
    """Job is held; it will not run until released by a user or administrator."""

    M = 'moved'
    """Job was moved to another server."""

    Q = 'queued'
    """Job is queued and eligible to run or be routed."""

    R = 'running'
    """Job is currently running."""

    S = 'suspended'
    """Job has been suspended by the scheduler; it is not currently running."""

    T = 'transition'
    """Job is in transition to or from a server."""

    U = 'unknown'
    """Job state is unknown, possibly due to communication issues with execution nodes."""

    W = 'waiting'
    """Job is waiting for its requested execution time to be reached or is delayed due to stage-in failure."""

    X = 'exited'
    """Subjobs only; subjob has finished (expired)."""
