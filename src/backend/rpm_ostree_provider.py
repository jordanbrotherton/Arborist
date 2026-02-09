from gi.repository import Gio
from typing import List
from .deployment import Deployment
from .atomic_provider import AtomicProvider


class RPMOSTreeProvider(AtomicProvider):
    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        self.proxy = Gio.DBusProxy.new_sync(
            self.bus,
            Gio.DBusProxyFlags.NONE,
            None,
            'org.projectatomic.rpmostree1',
            '/org/projectatomic/rpmostree1/Sysroot',
            'org.projectatomic.rpmostree1.Sysroot',
            None
        )

    def get_deployments(self) -> List[Deployment]:
        deployments_property = self.proxy.get_cached_property('Deployments')

        if not deployments_property:
            return []

        data = deployments_property.unpack()

        return [
            Deployment(
                id=item['id'],
                checksum=item['checksum'],
                version=item['version'],
                osname=item['osname'],
                booted=item.get('booted', False),
                staged=item.get('staged', False),
                pinned=item.get('pinned', False)
            ) for item in data
        ]
