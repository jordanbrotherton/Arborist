from dataclasses import dataclass


@dataclass
class Deployment:
    """
    Class that solely holds Atomic deployment data.
    """
    id: str  # Seems to only be '{osname}-{checksum}' on Silverblue
    origin: str
    checksum: str
    version: str
    osname: str

    pinned: bool
    booted: bool
    staged: bool
