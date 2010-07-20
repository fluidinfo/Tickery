# Copyright 2010 Fluidinfo Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.ScrollPanel import ScrollPanel
from pyjamas.ui.Grid import Grid

import server


class Queued(HorizontalPanel):
    def __init__(self):
        HorizontalPanel.__init__(self, Spacing=4)
        self.add(Label('Queued:', StyleName='section'))
        s = ScrollPanel()
        self.add(s)
        v = VerticalPanel()
        s.add(v)
        self.queued = Grid(StyleName='users')
        v.add(self.queued)
        self.button = Button('Refresh', self, StyleName='refresh')
        self.add(self.button)
        self.err = Label()
        self.add(self.err)
        self.update()

    def update(self):
        remote = server.AdminService()
        id = remote.getQueued(self)
        if id < 0:
            self.err.setText('oops: could not call getQueued')

    def onRemoteResponse(self, result, request_info):
        self.button.setEnabled(True)
        self.queued.clear()
        if not result:
            self.queued.resize(1, 1)
            self.queued.setText(0, 0, 'No users are queued for addition.')
        else:
            self.queued.resize(len(result) + 1, 4)
            self.queued.setText(0, 0, 'Pos')
            self.queued.setText(0, 1, 'Name')
            self.queued.setText(0, 2, 'Friends')
            self.queued.setText(0, 3, 'Queued at')
            row = 1
            for name, nFriends, time in result:
                self.queued.setText(row, 0, row)
                self.queued.setText(row, 1, name)
                self.queued.setText(row, 2, nFriends)
                self.queued.setText(row, 3, time)
                row += 1

    def onRemoteError(self, code, message, request_info):
        self.button.setEnabled(True)
        self.err.setText('Could not getQueued: ' + message)

    def onClick(self, sender):
        self.err.setText('')
        self.button.setEnabled(False)
        self.update()
