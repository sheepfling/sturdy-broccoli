from __future__ import annotations


class FOMResolutionError(ValueError):
    """Raised when a FOM/MIM module designator cannot be resolved or parsed.

    ``kind`` distinguishes open-vs-read failures so the RTI layer can map them
    to the corresponding HLA exception family instead of collapsing both cases
    into a single generic resolution error.
    """

    def __init__(self, message: str, *, kind: str = "open"):
        super().__init__(message)
        self.kind = kind


class FOMMergeError(ValueError):
    """Raised when FOM modules cannot be merged into a single FDD catalog."""
