from gettext import gettext as _

from gi.repository import Adw
from gi.repository import Gtk


class TaskProgress(Adw.MessageDialog):
    """
    Generic widget shared for any transaction.
    """
    def __init__(self, parent, heading: str, body: str):
        super().__init__(transient_for=parent, heading=heading, body=body)
        self.set_body_use_markup(True)

        self.base_body = body

        self.scroll_view = Gtk.ScrolledWindow(
            min_content_height=300,
            min_content_width=400,
            has_frame=True
        )

        self.source_view = Gtk.TextView(
            editable=False,
            monospace=True,
            wrap_mode=Gtk.WrapMode.WORD_CHAR,
            cursor_visible=False
        )
        self.scroll_view.set_child(self.source_view)

        self.set_extra_child(self.scroll_view)

    async def run_task(self, async_func, *args):
        self.present()
        try:
            await async_func(*args, self._on_body_change)

            self.set_heading(_("Finished"))
            self.set_body(
                _("Action has completed.")
            )
            self.add_response("close", _("Close"))
            self.set_response_appearance(
                "close",
                Adw.ResponseAppearance.SUGGESTED
            )
        except Exception as e:
            self.set_heading(_("Failed"))
            self.set_body(_("The transaction failed."))
            self._on_body_change(str(e))
            self.add_response("close", _("Close"))
            self.set_response_appearance(
                "close",
                Adw.ResponseAppearance.SUGGESTED
            )

    def _on_body_change(self, body: str):
        buffer = self.source_view.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, f"\n{body}")
        mark = buffer.get_insert()
        self.source_view.scroll_mark_onscreen(mark)
