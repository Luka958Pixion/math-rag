from enum import Enum


class PBSProJoinPath(str, Enum):
    """
    PBS Pro 2024.1.0 Join Path Options

    Reference:
        https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf
    """

    OE = 'oe'
    """Merge stderr into stdout. Both appear in the standard output file."""

    EO = 'eo'
    """Merge stdout into stderr. Both appear in the standard error file."""

    NONE = 'n'
    """Do not merge stdout and stderr. Keep output and error separate."""
