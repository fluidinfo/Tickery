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


class FriendsLimit(HorizontalPanel):
    def __init__(self):
        HorizontalPanel.__init__(self, Spacing=4)
        self.add(Label('Friends limit:', StyleName='section'))
        self.value = Label()
        self.add(self.value)
        self.newValue = TextBox()
        self.newValue.setMaxLength(5)
        self.newValue.setVisibleLength(5)
        self.add(self.newValue)
        self.update = Button('Update', FriendsUpdate(self))
        self.add(self.update)
        displayer = FriendsDisplay(self)
        self.refresh = Button('Refresh', displayer, StyleName='refresh')
        self.add(self.refresh)
        self.err = Label()
        self.add(self.err)
        remote = server.AdminService()
        id = remote.getFriendsLimit(displayer)
        if id < 0:
            self.err.setText('oops: could not call getFriendsLimit')


class FriendsDisplay(object):
    def __init__(self, sender):
        self.sender = sender
                 
    def onClick(self, sender):
        self.sender.err.setText('')
        self.sender.refresh.setEnabled(False)
        remote = server.AdminService()
        id = remote.getFriendsLimit(self)
        if id < 0:
            self.err.setText('oops: could not call getFriendsLimit')

    def onRemoteResponse(self, result, request_info):
        self.sender.refresh.setEnabled(True)
        self.sender.value.setText(result)

    def onRemoteError(self, code, message, request_info):
        self.sender.refresh.setEnabled(True)
        self.sender.err.setText('Could not getFriendsLimit: ' + message)


class FriendsUpdate(object):
    def __init__(self, sender):
        self.sender = sender
                 
    def onClick(self, sender):
        self.sender.err.setText('')
        value = self.sender.newValue.getText().strip()
        if value == '':
            return
        else:
            self.value = value
            self.sender.update.setEnabled(False)
            remote = server.AdminService()
            id = remote.setFriendsLimit(value, self)
            if id < 0:
                self.sender.err.setText('oops: could not setFriendsLimit')
            
    def onRemoteResponse(self, result, request_info):
        self.sender.update.setEnabled(True)
        self.sender.value.setText(self.value)

    def onRemoteError(self, code, message, request_info):
        self.sender.update.setEnabled(True)
        self.sender.err.setText('Could not setQueueWidth: ' + message)
