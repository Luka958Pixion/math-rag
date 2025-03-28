from enum import Enum


class PBSProMailPoints(str, Enum):
    """
    PBS Pro 2024.1.0 Mail Points

    Reference:
        https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf
    """

    ABORT = 'a'
    """Send mail when the job is aborted."""

    BEGIN = 'b'
    """Send mail at the beginning of the job."""

    END = 'e'
    """Send mail at the end of the job."""

    SUBJOBS = 'j'
    """Send mail for subjobs. Must be combined with 'a', 'b', or 'e'."""

    NONE = 'n'
    """Do not send mail. Cannot be combined with other options."""
