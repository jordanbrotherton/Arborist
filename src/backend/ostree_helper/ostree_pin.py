import sys
import gi

gi.require_version('OSTree', '1.0')
from gi.repository import OSTree


def pin(checksum: str):
    """Elevated OSTree helper function.
       Pins a supplied deployment.

    Args:
        checksum (str): The checksum of the deployment to toggle.
    """
    sysroot = OSTree.Sysroot.new_default()

    sysroot.set_mount_namespace_in_use()

    sysroot.load()
    deployments = sysroot.get_deployments()

    current_deployment = None

    for deployment in deployments:
        if deployment.get_csum() == checksum:
            current_deployment = deployment
            break

    if not current_deployment:
        raise Exception("Deployment not found.")

    new_status = not current_deployment.is_pinned()
    sysroot.deployment_set_pinned(current_deployment, new_status)
    sysroot.write_deployments(deployments)


if __name__ == "__main__":
    pin(sys.argv[1])
