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

import server


class QueueSize(HorizontalPanel):

    def __init__(self):
        HorizontalPanel.__init__(self, Spacing=4)
        self.add(Label('Queue size:', StyleName='section'))
        self.underway = Label()
        self.add(self.underway)
        self.queued = Label()
        self.add(self.queued)
        self.button = Button('Refresh', self, StyleName='refresh')
        self.add(self.button)
        self.err = Label()
        self.add(self.err)
        self.update()

    def update(self):
        remote = server.AdminService()
        id = remote.queueSize(self)
        if id < 0:
            self.err.setText('oops: could not call getQueueSize')

    def onRemoteResponse(self, result, request_info):
        self.button.setEnabled(True)
        underway, queued = result
        self.underway.setText('Underway: %d' % underway)
        self.queued.setText('Queued: %d' % queued)

    def onRemoteError(self, code, message, request_info):
        self.button.setEnabled(True)
        self.err.setText('Could not getQueueWidth: ' + message)

    def onClick(self, sender):
        self.err.setText('')
        self.button.setEnabled(False)
        self.update()
