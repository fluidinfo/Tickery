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


class QueueWidth(HorizontalPanel):
    def __init__(self):
        HorizontalPanel.__init__(self, Spacing=4)
        self.add(Label('Queue width:', StyleName='section'))
        self.value = Label()
        self.add(self.value)
        self.newValue = TextBox()
        self.newValue.setMaxLength(2)
        self.newValue.setVisibleLength(2)
        self.add(self.newValue)
        self.update = Button('Update', WidthUpdate(self))
        self.add(self.update)
        displayer = WidthDisplay(self)
        self.refresh = Button('Refresh', displayer, StyleName='refresh')
        self.add(self.refresh)
        self.err = Label()
        self.add(self.err)
        remote = server.AdminService()
        id = remote.getQueueWidth(displayer)
        if id < 0:
            self.err.setText('oops: could not call getQueueWidth')


class WidthDisplay(object):
    def __init__(self, queueWidth):
        self.sender = queueWidth
                 
    def onClick(self, sender):
        self.sender.err.setText('')
        self.sender.refresh.setEnabled(False)
        remote = server.AdminService()
        id = remote.getQueueWidth(self)
        if id < 0:
            self.sender.err.setText('oops: could not call getQueueWidth')

    def onRemoteResponse(self, result, request_info):
        self.sender.refresh.setEnabled(True)
        self.sender.value.setText(result)

    def onRemoteError(self, code, message, request_info):
        self.sender.refresh.setEnabled(True)
        self.sender.err.setText('Could not getQueueWidth: ' + message)


class WidthUpdate(object):
    def __init__(self, queueWidth):
        self.sender = queueWidth
                 
    def onClick(self, sender):
        self.sender.err.setText('')
        value = self.sender.newValue.getText().strip()
        if value == '':
            return
        else:
            self.value = value
            self.sender.update.setEnabled(False)
            remote = server.AdminService()
            id = remote.setQueueWidth(value, self)
            if id < 0:
                self.sender.err.setText('oops: could not setQueueWidth')
            
    def onRemoteResponse(self, result, request_info):
        self.sender.update.setEnabled(True)
        self.sender.value.setText(self.value)

    def onRemoteError(self, code, message, request_info):
        self.sender.update.setEnabled(True)
        self.sender.err.setText('Could not setQueueWidth: ' + message)
