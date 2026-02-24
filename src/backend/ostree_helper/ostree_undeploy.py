import sys
import gi

gi.require_version('OSTree', '1.0')
from gi.repository import OSTree


def undeploy(checksum: str):
    """Elevated OSTree helper function.
       Undeploys a supplied deployment.

    Args:
        checksum (str): The checksum of the deployment to undeploy.

    Raises:
        Exception: If the deployment is live (booted or staged).
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

    booted = sysroot.get_booted_deployment()

    is_active = booted and (booted.get_csum() == current_deployment.get_csum())

    if (is_active or current_deployment.is_staged()):
        raise Exception("Deployment is booted or staged.")

    new_deployments = []
    for deployment in deployments:
        if deployment.get_csum() != checksum:
            new_deployments.append(deployment)

    sysroot.write_deployments(new_deployments)
    sysroot.cleanup()


if __name__ == "__main__":
    undeploy(sys.argv[1])
