from dataclasses import dataclass


@dataclass
class Deployment:
    """
    Class that solely holds Atomic deployment data.
    """
    id: str  # Seems to only be '{osname}-{checksum}' on Silverblue
    origin: str  # Seems to be used on Silverblue
    container_image_reference: str  # Seems to be used in uBlue instead
    checksum: str
    version: str
    osname: str

    pinned: bool
    booted: bool
    staged: bool
