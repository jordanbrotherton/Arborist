from abc import ABC, abstractmethod
from typing import Callable, List

from .deployment import Deployment


class AtomicProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Determines if the provider is able to be used on the system.

        Returns:
            bool: If the provider is available in the system.
        """
        pass

    @abstractmethod
    async def setup(self):
        """
        Performs any initial setup with the provider.
        """
        pass

    @abstractmethod
    async def get_deployments(self) -> List[Deployment]:
        """Obtains and returns a list of Atomic deployments.

        Returns:
            List[Deployment]: A list of the fetched deployments.
        """
        pass

    @abstractmethod
    async def pin_deployment(
            self, checksum: str, body_method: Callable[[str], None]):
        """Pins/unpins a deployment.

        Args:
            checksum (str): The checksum of the deployment to toggle.
            body_method (Callable[[str], None]): The _on_body_change method of
                                                 the progress.
        """
        pass

    @abstractmethod
    async def undeploy_deployment(
            self, checksum: str, body_method: Callable[[str], None]):
        """Undeploys a provided deployment.

        Args:
            checksum (str): The checksum of the deployment to undeploy.
            body_method (Callable[[str], None]): The _on_body_change method of
                                                 the progress.
        """
        pass

    @abstractmethod
    async def rollback(self, body_method: Callable[[str], None]):
        """Triggers a rollback.

        Args:
            body_method (Callable[[str], None]): The _on_body_change method of
                                                 the progress.
        """
        pass

    @abstractmethod
    async def set_default(
            self, checksum: str, body_method: Callable[[str], None]):
        """Sets a deployment as default.

        Args:
            checksum (str): The checksum of the deployment to set as default.
            body_method (Callable[[str], None]): The _on_body_change method of
                                                 the progress.
        """
        pass

    @abstractmethod
    async def upgrade(self, body_method: Callable[[str], None]):
        """Upgrades the system.

        Args:
           body_method (Callable[[str], None]): The _on_body_change method of
                                                 the progress.
        """
        pass

    @abstractmethod
    async def rebase(self, remote: str, body_method: Callable[[str], None]):
        """Rebases system to provided remote.

        Args:
            remote (str): The remote to rebase to.
            body_method (Callable[[str], None]): The _on_body_change method of
                                                 the progress.
        """
        pass
