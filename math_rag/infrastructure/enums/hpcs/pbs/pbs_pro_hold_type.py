from enum import Enum


class PBSProHoldType(str, Enum):
    """
    PBS Pro 2024.1.0 Hold types

    Reference:
        https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf
    """

    USER = 'u'
    """User hold — can be set by the job owner, operator, manager, administrator, or root."""

    OTHER = 'o'
    """Other hold — can be set by the operator, manager, administrator, or root."""

    SYSTEM = 's'
    """System hold — can be set by manager, administrator, root, or PBS (e.g. job dependency)."""

    NONE = 'n'
    """No hold applied — the job is not currently on hold."""

    BAD_PASSWORD = 'p'
    """Bad password hold — can be set by the administrator or root (e.g. invalid credentials)."""
