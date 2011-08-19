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


class PauseResume(HorizontalPanel):
    def __init__(self):
        HorizontalPanel.__init__(self, Spacing=4)
        self.add(Label('Dispatch:', StyleName='section'))
        self.pause = Button('Pause', self)
        self.add(self.pause)
        self.resume = Button('Resume', self)
        self.add(self.resume)
        self.refresh = Button('Refresh', self, StyleName='refresh')
        self.add(self.refresh)
        self.err = Label()
        self.add(self.err)
        self._refresh()

    def _refresh(self):
        self.refresh.setEnabled(False)
        self.pause.setEnabled(False)
        self.resume.setEnabled(False)
        remote = server.AdminService()
        id = remote.queuePaused(self)
        if id < 0:
            self.err.setText('oops: could not call getQueueSize')

    def onClick(self, sender):
        self.err.setText('')
        if sender is self.refresh:
            self._refresh()
        elif sender is self.pause:
            self._pause()
        else:
            self._resume()

    def _pause(self):
        remote = server.AdminService()
        id = remote.pause(Paused(self))
        if id < 0:
            self.err.setText('oops: could not call pause.')

    def _resume(self):
        remote = server.AdminService()
        id = remote.resume(Resumed(self))
        if id < 0:
            self.err.setText('oops: could not call resume.')

    def onRemoteResponse(self, paused, request_info):
        self.refresh.setEnabled(True)
        if paused:
            self.resume.setEnabled(True)
        else:
            self.pause.setEnabled(True)

    def onRemoteError(self, code, message, request_info):
        self.refresh.setEnabled(True)
        self.err.setText('Error from queuePaused: ' + message)


class Paused(object):
    def __init__(self, sender):
        self.sender = sender

    def onRemoteResponse(self, result, request_info):
        self.sender.resume.setEnabled(True)
        self.sender.pause.setEnabled(False)

    def onRemoteError(self, code, message, request_info):
        self.sender.pause.setEnabled(True)
        self.sender.err.setText('Could not pause: ' + message)


class Resumed(object):
    def __init__(self, sender):
        self.sender = sender

    def onRemoteResponse(self, result, request_info):
        self.sender.pause.setEnabled(True)
        self.sender.resume.setEnabled(False)

    def onRemoteError(self, code, message, request_info):
        self.sender.resume.setEnabled(True)
        self.sender.err.setText('Could not resume: ' + message)
