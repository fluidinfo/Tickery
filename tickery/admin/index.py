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

import pyjd
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.Label import Label
from pyjamas.ui.Image import Image

import width
import size
import friends
import results
import directadd
import pause
import underway
import queued
import requests
import cancel


class Admin(VerticalPanel):
    def __init__(self):
        VerticalPanel.__init__(self, Spacing=8, StyleName='admin')
        self.setWidth('100%')
        self.add(Image('tickery.png'))
        self.add(Label('Welcome, root user.', StyleName='title'))

        self.add(width.QueueWidth())
        self.add(size.QueueSize())
        self.add(requests.MaxRequestsLimit())
        self.add(friends.FriendsLimit())
        self.add(results.ResultsLimit())
        self.add(directadd.DirectAdd())
        self.add(directadd.BulkDirectAdd())
        self.add(cancel.Cancel())
        self.add(pause.PauseResume())
        self.add(underway.Underway())
        self.add(queued.Queued())


if __name__ == '__main__':
    pyjd.setup('http://127.0.0.1:6969/public')
    RootPanel().add(Admin())
    pyjd.run()


### Local Variables:
### eval: (rename-buffer "index.py (admin)")
### End:
