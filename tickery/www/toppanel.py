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

import banner

from pyjamas.ui.Grid import Grid


class TopPanel(Grid):
    def __init__(self, loginPanel):
        Grid.__init__(self, 1, 1, StyleName='top-panel')
        self.loginPanel = loginPanel
        self.banner = banner.Banner()
        self.setWidget(0, 0, self.banner)
        formatter = self.getCellFormatter()
        formatter.setHorizontalAlignment(0, 0, 'left')
        formatter.setVerticalAlignment(0, 0, 'top')

    def loggedIn(self):
        return self.loginPanel.loggedIn
