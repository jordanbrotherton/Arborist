from abc import ABC, abstractmethod
from typing import List
from .deployment import Deployment


class AtomicProvider(ABC):
    @abstractmethod
    def get_deployments(self) -> List[Deployment]:
        """
        Obtains and returns a list of Atomic deployments.
        """
        pass
