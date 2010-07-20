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

import utils, server

from pyjamas.ui.Image import Image
from pyjamas.ui.HTML import HTML
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui import HasAlignment


class Banner(VerticalPanel):
    def __init__(self):
        VerticalPanel.__init__(self,
                               HorizontalAlignment=HasAlignment.ALIGN_LEFT,
                               StyleName='banner-panel')
        self.add(Image('tickery.png', StyleName='banner-image'))
        strapline = HTML(
            '''Explore <a href="http://twitter.com">Twitter</a> with
            <a href="http://fluidinfo.com/fluiddb">FluidDB</a>''',
            StyleName='strapline')
        self.add(strapline)

        # To add the "Tracking XXX users" label, uncomment the following
        # three lines, and rename xxx_update to update below.
        #
        # self.countLabel = HTML(StyleName='tracking')
        # self.add(self.countLabel)
        # self.update()

    def xxx_update(self):
        remote = server.TickeryService()
        id = remote.nUsers(self)
        if id < 0:
            self.add(HTML('oops'))

    def _showCount(self, n):
        if isinstance(n, int):
            n = utils.splitthousands(n)
        self.countLabel.setHTML('Tracking %s users' % n)

    def onRemoteResponse(self, response, request_info):
        self._showCount(response)

    def onRemoteError(self, code, message, request_info):
        self.countLabel.setHTML('Tracking 3 billion users')
        self.add(HTML('Server error %d: %s' % (code, message)))
