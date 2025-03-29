from enum import Enum


class PBSProKeepFiles(str, Enum):
    """
    PBS Pro 2024.1.0 Keep_Files Options

    Reference:
        https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf
    """

    STDOUT = 'o'
    """Retain only the standard output stream on the execution host."""

    STDERR = 'e'
    """Retain only the standard error stream on the execution host."""

    STDOUT_STDERR = 'oe'
    """Retain both standard output and standard error streams."""

    STDERR_STDOUT = 'eo'
    """Retain both standard error and standard output streams (equivalent to 'oe')."""

    DIRECT = 'd'
    """Write output and error directly to their final destination."""

    STDOUT_STDERR_DIRECT = 'oed'
    """Retain both output and error streams, and write directly to final destination (non-standard, observed in output)."""

    NONE = 'n'
    """Do not retain output or error files; return them to the submission host."""
