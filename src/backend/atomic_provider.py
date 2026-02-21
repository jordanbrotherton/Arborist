from abc import ABC, abstractmethod
from typing import List
from .deployment import Deployment


class AtomicProvider(ABC):
    @abstractmethod
    async def setup():
        """
        Performs any initial setup with the provider.
        """
        pass

    @abstractmethod
    async def get_deployments(self) -> List[Deployment]:
        """
        Obtains and returns a list of Atomic deployments.
        """
        pass

    @abstractmethod
    async def pin_deployment(self, idx: int, pinned: bool):
        """
        Pins/unpins a deployment.
        """
        pass

    @abstractmethod
    async def undeploy_deployment(self, idx: int):
        """
        Undeploys a provided deployment.
        """
        pass

    @abstractmethod
    async def rollback(self, progress_ui):
        """
        Triggers a rollback.
        """
        pass

    @abstractmethod
    async def set_default(self, idx: int):
        """
        Sets a deployment as default.
        """
        pass

    @abstractmethod
    async def upgrade(self):
        """
        Upgrades the system.
        """
        pass

    @abstractmethod
    async def rebase(self, remote: str):
        """
        Rebases system to provided remote.
        """
        pass
