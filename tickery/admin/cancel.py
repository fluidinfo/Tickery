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
from pyjamas.ui.TextBox import TextBox

import server


class Cancel(HorizontalPanel):
    def __init__(self):
        HorizontalPanel.__init__(self, Spacing=4)
        self.add(Label('Cancel:', StyleName='section'))
        self.name = TextBox()
        self.name.setMaxLength(18)
        self.name.setVisibleLength(18)
        self.add(self.name)
        self.cancel = Button('Do it', self)
        self.add(self.cancel)
        self.err = Label()
        self.add(self.err)

    def onClick(self, sender):
        self.err.setText('')
        name = self.name.getText().strip()
        if name == '':
            return
        else:
            self.cancel.setEnabled(False)
            remote = server.AdminService()
            id = remote.cancel(name, self)
            if id < 0:
                self.err.setText('oops: could not cancel')

    def onRemoteResponse(self, result, request_info):
        self.cancel.setEnabled(True)
        self.name.setText('')

    def onRemoteError(self, code, message, request_info):
        self.cancel.setEnabled(True)
        self.err.setText('Could not cancel: ' + message['data']['message'])
