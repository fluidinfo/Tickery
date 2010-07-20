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

import toppanel, simple, intermediate, advanced, about, login

from pyjamas.ui.TabPanel import TabPanel
from pyjamas.ui.HTML import HTML
from pyjamas import Window


class Tabs(TabPanel):
    def __init__(self):
        TabPanel.__init__(self, StyleName='tab-panel', Width='100%')
        loginPanel = login.LoginPanel()
        topPanel = toppanel.TopPanel(loginPanel)
        self.simple = simple.Simple(topPanel)
        self.intermediate = intermediate.Intermediate(topPanel)
        self.advanced = advanced.Advanced(topPanel)
        self.about = about.About(topPanel)
        
        self.add(self.simple, 'Simple')
        self.add(self.intermediate, 'Intermediate')
        self.add(self.advanced, 'Advanced')
        self.add(self.about, 'About')
        self.add(HTML('&nbsp;'), None)
        self.add(HTML('&nbsp'), loginPanel)
        
    def setDefaultTab(self):
        args = Window.getLocation().getSearchDict()
        wantedTab = args.get('tab', self.simple.tabName).lower()
            
        if wantedTab == self.intermediate.tabName:
            self.selectTab(1)
        elif wantedTab == self.advanced.tabName:
            self.selectTab(2)
        elif wantedTab == self.about.tabName:
            self.selectTab(3)
        else:
            self.selectTab(0)

    def adjustSize(self, width, height):
        self.simple.adjustSize(width, height)
        self.intermediate.adjustSize(width, height)
        self.advanced.adjustSize(width, height)

    def onBeforeTabSelected(self, sender, tabindex):
        return tabindex <= 3
