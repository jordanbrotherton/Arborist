from gettext import gettext as _
from gi.repository import Adw, Gtk, GObject, Gio


@Gtk.Template(
    resource_path='/io/github/jordanbrotherton/arborist/ui/deployment_row.ui')
class DeploymentRow(Adw.ActionRow):
    __gtype_name__ = 'DeploymentRow'

    @GObject.Signal
    def pin_called(self):
        pass

    @GObject.Signal
    def set_default_called(self):
        pass

    @GObject.Signal
    def undeploy_called(self):
        pass

    pinned_image = Gtk.Template.Child("pinned")
    staged_image = Gtk.Template.Child("staged")
    booted_image = Gtk.Template.Child("active")

    def __init__(self, deployment, **kwargs):
        super().__init__(**kwargs)

        self.init_template()
        
        if deployment.version:
            self.set_title(deployment.version)
        else:
            self.set_title(_("No version data"))

        if deployment.origin:
            self.set_subtitle(deployment.origin)
        elif deployment.container_image_reference:
            self.set_subtitle(deployment.container_image_reference)
        elif deployment.id:
            self.set_subtitle(deployment.id)
        elif deployment.checksum:
            self.set_subtitle(deployment.checksum)
        else:
            self.set_subtitle(_("No additional data"))

        self.deployment = deployment

        self.pinned_image.set_visible(deployment.pinned)
        self.staged_image.set_visible(deployment.staged)
        self.booted_image.set_visible(deployment.booted)

        self.action_group = Gio.SimpleActionGroup.new()
        self.insert_action_group("row", self.action_group)

        pin_action = Gio.SimpleAction.new("pin", None)
        pin_action.connect("activate", self._on_pin_clicked)
        self.action_group.add_action(pin_action)

        default_action = Gio.SimpleAction.new("set_default", None)
        default_action.connect("activate", self._on_set_default_clicked)
        self.action_group.add_action(default_action)

        if not (deployment.booted or deployment.staged or deployment.pinned):
            undeploy_action = Gio.SimpleAction.new("undeploy", None)
            undeploy_action.connect("activate", self._on_undeploy_clicked)
            self.action_group.add_action(undeploy_action)

    def _on_pin_clicked(self, action, parameter):
        self.emit('pin_called')

    def _on_undeploy_clicked(self, action, parameter):
        self.emit('undeploy_called')

    def _on_set_default_clicked(self, action, parameter):
        self.emit('set_default_called')
