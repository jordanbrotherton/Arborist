import asyncio
import os
import sys

from dbus_fast.aio import MessageBus
from dbus_fast import Variant
from dbus_fast import BusType
from typing import List
from gi.repository import Gio

from .deployment import Deployment
from .atomic_provider import AtomicProvider

BUS_NAME = 'org.projectatomic.rpmostree1'

SYSROOT_PATH = '/org/projectatomic/rpmostree1/Sysroot'
SYSROOT_NAME = 'org.projectatomic.rpmostree1.Sysroot'

DBUS_PROPS_NAME = 'org.freedesktop.DBus.Properties'

OS_NAME = 'org.projectatomic.rpmostree1.OS'

TRANSACTION_NAME = 'org.projectatomic.rpmostree1.Transaction'


class RPMOSTreeDBusProvider(AtomicProvider):
    """
    An AtomicProvider utilizing the D-Bus daemon of rpm-ostree.
    Additionally utilizes the ostree C library for actions it does not handle.
    """
    def is_available(self) -> bool:
        try:
            bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            proxy = Gio.DBusProxy.new_sync(
                bus,
                Gio.DBusProxyFlags.NONE,
                None,
                BUS_NAME,
                SYSROOT_PATH,
                SYSROOT_NAME,
                None
            )
            return proxy.get_name_owner() is not None
        except Exception as e:
            print(f"[RPM-OSTree] - Not available. Error: {str(e)}")
            return False

    async def setup(self):
        self.bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        self.sysroot_introspection = await self.bus.introspect(
            BUS_NAME,
            SYSROOT_PATH
        )
        self.sysroot_proxy = self.bus.get_proxy_object(
            BUS_NAME,
            SYSROOT_PATH,
            self.sysroot_introspection
        )
        self.sysroot_interface = self.sysroot_proxy.get_interface(
            SYSROOT_NAME
        )
        self.properties_interface = self.sysroot_proxy.get_interface(
            DBUS_PROPS_NAME
        )
        self.properties_interface.on_properties_changed(
            self._on_properties_changed
        )

    async def get_deployments(self) -> List[Deployment]:
        data = await self.sysroot_interface.get_deployments()

        if not data:
            return []

        return [
            Deployment(
                id=item['id'].value,
                origin=item['origin'].value,
                checksum=item['checksum'].value,
                version=item['version'].value,
                osname=item['osname'].value,
                booted=item['booted'].value,
                staged=item['staged'].value,
                pinned=item['pinned'].value
            ) for item in data
        ]

    async def pin_deployment(self, checksum: str, body_method):
        await self._run_ostree("ostree_pin.py", body_method, checksum)

    async def undeploy_deployment(self, checksum: str, body_method):
        await self._run_ostree("ostree_undeploy.py", body_method, checksum)

    async def rollback(self, body_method):
        os_interface = await self._get_os_interface()

        rollback_path = await os_interface.call_rollback({})
        await self._run_transaction(rollback_path, body_method)

    async def set_default(self, checksum: str, body_method):
        await self._run_ostree("ostree_set_default.py", body_method, checksum)

    async def upgrade(self, body_method):
        os_interface = await self._get_os_interface()

        upgrade_path = await os_interface.call_upgrade({})
        await self._run_transaction(upgrade_path, body_method)

    async def rebase(self, remote: str, body_method):
        os_interface = await self._get_os_interface()

        rebase_path = await os_interface.call_rebase({}, remote, [])
        await self._run_transaction(rebase_path, body_method)

    async def _on_properties_changed(self,
                                     interface_name: str,
                                     changed_properties: dict,
                                     invalidated_properties: List[str]):
        if "Deployments" in changed_properties:
            self.deployments_changed.emit()

    async def _get_os_interface(self, os_name: str = ""):
        """Fetches the OS DBus interface for rpm-ostree.

        Args:
            os_name (str, optional): The os-name of the deployment.
                                     Defaults to "".
        """
        if os_name:
            os_path = await self.sysroot_interface.get_os({os_name})
        else:
            os_path = await self.sysroot_interface.get_booted()

        os_introspection = await self.bus.introspect(
            BUS_NAME,
            os_path
        )

        os_proxy = self.bus.get_proxy_object(
            BUS_NAME,
            os_path,
            os_introspection
        )
        os_interface = os_proxy.get_interface(OS_NAME)
        return os_interface

    async def _run_ostree(self, helper: str, body_method, *args):
        """Calls an external OSTree helper script that requires elevation.

        Args:
            helper (str): The filename of the ostree-helper script.
            body_method (Callable[[str], None]): The _on_body_change method of
                                                 the progress.

        Raises:
            Exception: When the helper script fails to run.
        """

        # Passes a helper through the Python interpreter to avoid FUSE errors.
        helper_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "ostree_helper",
            helper
        )

        with open(helper_path, 'r') as f:
            script_content = f.read()

        cmd = ["pkexec", sys.executable, "-"]
        for arg in args:
            cmd.append(str(arg))

        body_method(f"Executing {helper}...")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )

        process.stdin.write(script_content.encode())
        await process.stdin.drain()
        process.stdin.close()

        returncode = await process.wait()

        if returncode != 0:
            raise Exception(f"{helper} failed to run. Exit code: {returncode}")
        else:
            body_method(f"{helper} finished successfully.")

    async def _run_transaction(self, path: str, body_method):
        """Runs and monitors the rpm-ostree transaction.

        Args:
            path (str): The transaction path from the method.
            body_method (Callable[[str], None]): The _on_body_change method of
                                                 the progress.
        """
        options = {"id": Variant('s', 'arborist')}
        await self.sysroot_interface.call_register_client(options)
        transaction_bus = await MessageBus(bus_address=path).connect()
        try:
            introspection = await transaction_bus.introspect(BUS_NAME, '/')
            proxy_object = transaction_bus.get_proxy_object(
                BUS_NAME,
                '/',
                introspection
            )
            interface = proxy_object.get_interface(TRANSACTION_NAME)

            finished_future = asyncio.get_event_loop().create_future()

            def message_handler(message):
                if message.member == 'Message':
                    text = message.body[0]
                    body_method(text)
                elif message.member == 'Finished':
                    success, error_message = message.body
                    if not success:
                        finished_future.set_exception(Exception(error_message))
                    if not finished_future.done():
                        finished_future.set_result(True)
                return False

            transaction_bus.add_message_handler(message_handler)

            if await interface.call_start():
                await finished_future
        finally:
            transaction_bus.disconnect()
            await self.sysroot_interface.call_unregister_client(options)
