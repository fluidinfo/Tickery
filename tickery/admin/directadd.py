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
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Button import Button
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.TextBox import TextBox
from pyjamas.ui.TextArea import TextArea

import server


class DirectAdd(HorizontalPanel):
    def __init__(self):
        HorizontalPanel.__init__(self, Spacing=4)
        self.add(Label('Directly add:', StyleName='section'))
        self.name = TextBox()
        self.name.setMaxLength(18)
        self.name.setVisibleLength(18)
        self.add(self.name)
        self.update = Button('Add', self)
        self.add(self.update)
        self.err = Label()
        self.add(self.err)

    def onClick(self, sender):
        self.err.setText('')
        name = self.name.getText().strip()
        if name == '':
            return
        else:
            self.update.setEnabled(False)
            remote = server.AdminService()
            id = remote.directAddUser(name, self)
            if id < 0:
                self.err.setText('oops: could not add')

    def onRemoteResponse(self, result, request_info):
        self.update.setEnabled(True)

    def onRemoteError(self, code, message, request_info):
        self.update.setEnabled(True)
        self.err.setText('Could not add: ' + message['data']['message'])


class BulkDirectAdd(HorizontalPanel):
    def __init__(self):
        HorizontalPanel.__init__(self, Spacing=4)
        self.add(Label('Directly add in bulk:', StyleName='section'))
        self.names = TextArea(VisibleLines=5)
        self.add(self.names)
        self.update = Button('Add', self)
        self.add(self.update)
        self.err = HTML()
        self.add(self.err)

    def onClick(self, sender):
        self.err.setHTML('')
        names = self.names.getText().strip()
        if names == '':
            return
        else:
            self.update.setEnabled(False)
            remote = server.AdminService()
            id = remote.bulkAddUsers(names, self)
            if id < 0:
                self.err.setText('oops: could not add')

    def onRemoteResponse(self, result, request_info):
        self.update.setEnabled(True)
        self.err.setText('OK, adding.')

    def onRemoteError(self, code, message, request_info):
        self.update.setEnabled(True)
        self.err.setHTML('Errors:<br/>' +
                         '<br/>'.join(message['data']['message']))
