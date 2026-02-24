import asyncio
from gettext import gettext as _
from typing import Callable

from gi.repository import Adw, Gtk, Gio

from .widgets.deployment_row import DeploymentRow
from .widgets.task_progress import TaskProgress
from .backend.rpm_ostree_provider import RPMOSTreeDBusProvider


@Gtk.Template(resource_path='/io/github/jordanbrotherton/arborist/window.ui')
class ArboristWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ArboristWindow'

    window_view: Adw.ViewStack = Gtk.Template.Child()
    deployment_list: DeploymentRow = Gtk.Template.Child()
    upgrade_button: Gtk.Button = Gtk.Template.Child()
    rollback_button: Gtk.Button = Gtk.Template.Child()
    rebase_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.provider = RPMOSTreeDBusProvider()

        if self.provider.is_available():
            asyncio.ensure_future(self._setup_provider())

            self.upgrade_button.connect("clicked", self._on_upgrade_clicked)
            self.rollback_button.connect("clicked", self._on_rollback_clicked)
            self.rollback_button.connect("clicked", self._on_rebase_clicked)
        else:
            self.window_view.set_visible_child_name("status_page")
            self.upgrade_button.set_sensitive(False)
            self.rollback_button.set_sensitive(False)
            self.rebase_button.set_sensitive(False)

    async def _setup_provider(self):
        await self.provider.setup()
        await self._populate_deployments()
        self.window_view.set_visible_child_name("deployment_page")

    async def _populate_deployments(self):
        deployments = await self.provider.get_deployments()
        while (child := self.deployment_list.get_first_child()):
            self.deployment_list.remove(child)

        for data in deployments:
            row = DeploymentRow(data)
            row.connect('pin_called', self._on_pin_clicked)
            row.connect('set_default_called', self._on_set_default_clicked)
            row.connect('undeploy_called', self._on_undeploy_clicked)
            self.deployment_list.append(row)

    def _on_upgrade_clicked(self, button: Gtk.Button):
        # TODO - Add checking, and warn if automatic updates are enabled.
        dialog = TaskProgress(
            self,
            _("Upgrading"),
            _("Arborist is upgrading your OS...")
        )

        asyncio.ensure_future(self._run_task(dialog, self.provider.upgrade))

    def _on_rollback_clicked(self, button: Gtk.Button):
        dialog = TaskProgress(
            self,
            _("Rolling Back"),
            _("Arborist is swapping your deployment order...")
        )

        asyncio.ensure_future(self._run_task(dialog, self.provider.rollback))

    def _on_rebase_clicked(self, button: Gtk.Button):
        # TODO - Unstub rebase and ask for remote.
        dialog = TaskProgress(
            self,
            _("Rebasing"),
            _("Arborist is rebasing to a new image...")
        )

        asyncio.ensure_future(self._run_task(dialog, self.provider.rebase))

    def _on_pin_clicked(self, deployment_row: DeploymentRow):
        dialog = TaskProgress(
            self,
            _("Pin Toggling"),
            _("Arborist is toggling the pin of your deployment...")
        )

        asyncio.ensure_future(self._run_task(
            dialog,
            self.provider.pin_deployment,
            deployment_row.deployment.checksum)
        )

    def _on_set_default_clicked(self, deployment_row: DeploymentRow):
        dialog = TaskProgress(
            self,
            _("Setting as Default"),
            _("Arborist is moving your deployment to the top...")
        )

        asyncio.ensure_future(self._run_task(
            dialog,
            self.provider.set_default,
            deployment_row.deployment.checksum)
        )

    def _on_undeploy_clicked(self, deployment_row: DeploymentRow):
        choice_box = Adw.AlertDialog(
            heading=_("Danger!"),
            body=_("This action will permanently remove this deployment. "
                   "Caution is recommended.")
        )

        choice_box.add_response('confirm', _("Undeploy"))
        choice_box.add_response('cancel', _("Cancel"))

        choice_box.set_response_appearance(
            'confirm',
            Adw.ResponseAppearance.DESTRUCTIVE
        )

        choice_box.choose(
            self,
            None,
            self._on_undeploy_option_chosen,
            deployment_row
        )

    def _on_undeploy_option_chosen(self,
                                   dialog: Adw.AlertDialog,
                                   option: Gio.Task,
                                   deployment_row: DeploymentRow):
        choice = dialog.choose_finish(option)
        if choice == 'confirm':
            dialog = TaskProgress(
                self,
                _("Undeploying"),
                _("Arborist is removing your deployment...")
            )

            asyncio.ensure_future(self._run_task(
                dialog,
                self.provider.undeploy_deployment,
                deployment_row.deployment.checksum)
            )

    async def _run_task(self, dialog: TaskProgress, task: Callable, *args):
        """Executes a task in the provider backend.

        Args:
            dialog (TaskProgress): The TaskProgress dialog to run the task.
            task (Callable): The task to be executed.
        """
        await dialog.run_task(task, *args)
        await self.populate_deployments()
