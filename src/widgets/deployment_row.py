from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/io/github/jordanbrotherton/arborist/ui/deployment_row.ui')
class DeploymentRow(Adw.ActionRow):
    __gtype_name__ = 'DeploymentRow'

    pinned_image = Gtk.Template.Child("pinned")
    staged_image = Gtk.Template.Child("staged")
    booted_image = Gtk.Template.Child("active")

    def __init__(self, deployment, **kwargs):
        super().__init__(**kwargs)

        self.init_template()
        print(deployment)
        self.set_title(deployment.version)
        self.set_subtitle(deployment.id)

        self.pinned_image.set_visible(deployment.pinned)
        self.staged_image.set_visible(deployment.staged)
        self.booted_image.set_visible(deployment.booted)
