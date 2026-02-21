# window.py
#
# Copyright 2026 Jordan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
import asyncio
from gi.repository import Gtk
from .widgets.deployment_row import DeploymentRow
from .backend.rpm_ostree_provider import RPMOSTreeProvider


@Gtk.Template(resource_path='/io/github/jordanbrotherton/arborist/window.ui')
class ArboristWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ArboristWindow'

    deployment_list = Gtk.Template.Child()
    rollback_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.provider = RPMOSTreeProvider()

        asyncio.ensure_future(self.setup_provider())

        # self.rollback_button.connect("clicked", self.on_rollback_clicked)

    async def setup_provider(self):
        await self.provider.setup()
        await self.populate_deployments()

    async def populate_deployments(self):
        deployments = await self.provider.get_deployments()
        while (child := self.deployment_list.get_first_child()):
            self.deployment_list.remove(child)

        for data in deployments:
            row = DeploymentRow(data)
            self.deployment_list.append(row)

