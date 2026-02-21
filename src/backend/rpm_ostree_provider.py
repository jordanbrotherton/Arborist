from dbus_fast.aio import MessageBus
from dbus_fast import BusType
from typing import List
from .deployment import Deployment
from .atomic_provider import AtomicProvider


class RPMOSTreeProvider(AtomicProvider):
    async def setup(self):
        self.bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        self.sysroot_introspection = await self.bus.introspect(
            'org.projectatomic.rpmostree1',
            '/org/projectatomic/rpmostree1/Sysroot'
        )
        self.sysroot_proxy = self.bus.get_proxy_object(
            'org.projectatomic.rpmostree1',
            '/org/projectatomic/rpmostree1/Sysroot',
            self.sysroot_introspection
        )
        self.sysroot_interface = self.sysroot_proxy.get_interface(
            'org.projectatomic.rpmostree1.Sysroot'
        )

    async def get_deployments(self) -> List[Deployment]:
        data = await self.sysroot_interface.get_deployments()

        if not data:
            return []

        return [
            Deployment(
                id=item['id'].value,
                checksum=item['checksum'].value,
                version=item['version'].value,
                osname=item['osname'].value,
                booted=item['booted'].value,
                staged=item['staged'].value,
                pinned=item['pinned'].value
            ) for item in data
        ]

    def pin_deployment(self, idx: int, pinned: bool):
        pass

    def undeploy_deployment(self, idx: int):
        pass

    def rollback(self, progress_ui):
        pass

    def set_default(self, idx: int):
        pass

    def upgrade(self):
        pass

    def rebase(self, remote: str):
        pass
