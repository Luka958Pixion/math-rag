from enum import Enum


class PBSSubjobState(str, Enum):
    """
    PBS Pro 2022.1.1 Subjob States

    Reference:
        https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf
    """

    E = 'ending'
    """(5) Subjob is in the process of exiting."""

    F = 'finished'
    """(9) Subjob has completed execution."""

    Q = 'queued'
    """(1) Subjob is waiting in the queue."""

    R = 'running'
    """(4) Subjob is currently executing."""

    S = 'suspended'
    """(None; sub-state of R) Subjob is suspended."""

    U = 'suspended_by_keyboard'
    """(None; sub-state of R) Subjob is suspended due to keyboard activity."""

    X = 'exited'
    """(6) Subjob has expired or been deleted (completed or terminated)."""
