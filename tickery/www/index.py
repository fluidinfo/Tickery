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
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas import Timer, DeferredCommand, Window

import tabs, userlist, defaults


class Tickery(SimplePanel):
    def __init__(self):
        SimplePanel.__init__(self, StyleName='main-panel')
        self.setWidth('100%')
        self.tabs = tabs.Tabs()
        self.tabs.addTabListener(self)
        self.add(self.tabs)
        
        Window.addWindowResizeListener(self)
        DeferredCommand.add(self)

        args = Window.getLocation().getSearchDict()
        userlist.setSortKey(args.get('sort'))        
        userlist.setIconSize(args.get('icons'))        

    def onBeforeTabSelected(self, sender, tabIndex):
        return True

    def onTabSelected(self, sender, tabIndex):
        tab = self.tabs.getWidget(tabIndex)
        Timer.Timer(100, tab)
        tab.addTopPanel()

    def onLoad(self):
        self.tabs.setDefaultTab()

    def execute(self):
        self.onWindowResized(Window.getClientWidth(), Window.getClientHeight())

    def onWindowResized(self, width, height):
        self.tabs.adjustSize(width, height)


if __name__ == '__main__':
    pyjd.setup('http://127.0.0.1:%d/public' % defaults.TICKERY_SERVICE_PORT)
    RootPanel().add(Tickery())
    pyjd.run()

### Local Variables:
### eval: (rename-buffer "index.py (www)")
### End:
