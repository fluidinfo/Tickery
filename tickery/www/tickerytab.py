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

import urllib

import go, userlist, server, text, results, defaults

from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.Grid import Grid
from pyjamas.ui.HTMLPanel import HTMLPanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui import HasAlignment
from pyjamas import Window

from pyjamas.ui.ScrollPanel import ScrollPanel
from Popups import DialogBoxModal

POPUP_WIDTH = 700
POPUP_HEIGHT = 500


class InstructionBox(DialogBoxModal):
    def __init__(self, identifier, instructions):
        DialogBoxModal.__init__(self, identifier, autoHide=False)
        self.setWidth('%dpx' % POPUP_WIDTH)
        self.setHeight('%dpx' % POPUP_HEIGHT)
        self.scrollpanel = ScrollPanel(
            instructions, Width='100%', Height='%dpx' % (POPUP_HEIGHT - 30,))
        self.setWidget(self.scrollpanel)

    def onClick(self, sender):
        self.hide()


SHORT_INSTRUCTIONS = {
    # Don't put line breaks into the following strings. MSIE preserves them!
    'intermediate' :
    """Explore sets of Twitter friends by querying on their user names""",
    
    'advanced' :
    """Query Twitter friends & more with the full FluidDB query language""",
    }

HELP_TEXT = 'huh?'

def titleMaker(users):
    if users:
        nUsers = len(users)
        if nUsers > 1:
            plural = 's'
        else:
            plural = ''
        return 'Your query matches %s user%s:' % (nUsers, plural)
    else:
        return 'Results set is empty.'



class TickeryTab(VerticalPanel):

    process = None # Define in subclass.
    
    def __init__(self, topPanel, **kwargs):
        VerticalPanel.__init__(self,
                               HorizontalAlignment=HasAlignment.ALIGN_LEFT,
                               StyleName='tickery-tab',
                               **kwargs)
        self.topPanel = topPanel # don't add this yet!
        self.topGrid = Grid(1, 2, StyleName='tickery-tab-top-grid',
                            HorizontalAlignment=HasAlignment.ALIGN_LEFT)
        self.add(self.topGrid)
        self.autoActivate = False

    def addTopPanel(self):
        parent = self.topPanel.getParent()
        if parent:
            parent.remove(self.topPanel)
        self.topGrid.setWidget(0, 0, self.topPanel)
        formatter = self.topGrid.getCellFormatter()
        formatter.setAlignment(0, 0, 'left', 'top')
        formatter.setAlignment(0, 1, 'left', 'top')
        formatter.setWidth(0, 1, '100%')

    def onTimer(self, timerid):
        self.setInputFocus()
        if self.autoActivate:
            self.autoActivate = False
            self.process()


class LargeQueryTab(TickeryTab):

    # Define these in subclasses
    instructions = None
    instructionsTitle = None
    tabName = None
    defaultQuery = None
    
    def __init__(self, topPanel):
        TickeryTab.__init__(self, topPanel)
        # Get the query string and wanted tab, if any, from URL args.
        args = Window.getLocation().getSearchDict()
        query = args.get('query')
        wantedTab = args.get('tab')
        if wantedTab:
            wantedTab = wantedTab.lower()
        if query and wantedTab == self.tabName.lower():
            query = urllib.unquote_plus(query)
            self.autoActivate = True
        else:
            query = self.defaultQuery
            
        self.instructions.setHorizontalAlignment(HasAlignment.ALIGN_LEFT)
        self.instructions.setStyleName('instructions-popup')
        self.popup = InstructionBox(
            self.__class__.__name__, self.instructions)
        self.popup.setText(self.instructionsTitle)
        self.db = Button(HELP_TEXT, StyleName='help-button')
        self.db.addClickListener(self)

        huhId = HTMLPanel.createUniqueId()
        help = HTMLPanel('%s <span id="%s"></span>' %
                             (SHORT_INSTRUCTIONS[self.tabName], huhId),
                             StyleName='simple-instructions')
        help.add(self.db, huhId)
        
        self.goButton = go.GoButton(self)
        self.query = text.TextAreaFocusHighlight(Text=query,
                                                 VisibleLines=3,
                                                 StyleName='large-query-area')
        self.checkResult = HorizontalPanel(Spacing=4)
        
        mainGrid = Grid(2, 2, StyleName='tickery-tab-panel',
                        HorizontalAlignment=HasAlignment.ALIGN_LEFT)
        formatter = mainGrid.getCellFormatter()
        mainGrid.setWidget(0, 0, help)
        mainGrid.setWidget(1, 0, self.query)
        mainGrid.setWidget(1, 1, self.goButton)
        formatter.setHorizontalAlignment(0, 0, 'left')
        formatter.setHorizontalAlignment(1, 0, 'left')
        formatter.setAlignment(1, 1, 'left', 'bottom')
        self.topGrid.setWidget(0, 1, mainGrid)
        
        self.add(self.checkResult)
        self.results = userlist.UserListPanel(self, topPanel,
            HorizontalAlignment=HasAlignment.ALIGN_LEFT)
        self.add(self.results)

    def setInputFocus(self):
        self.query.setFocus(True)

    def clearResults(self):
        self.results.clear()

    def clearCheckResult(self):
        self.checkResult.clear()

    def onClick(self, sender):
        if sender == self.db:
            width = (Window.getClientWidth() - POPUP_WIDTH) / 2.0
            self.popup.setPopupPosition(width, 100)
            self.popup.show()
        else:
            self.process()

    def process(self):
        self.clearCheckResult()
        self.clearResults()
        text = self.query.getText()
        query = text.strip()
        if query:
            self.query.setCursorPos(len(text))
            self.goButton.setEnabled(False)
            checkWidget = results.ResultHandler(
                query, self, self.tabName, titleMaker)
            remote = server.TickeryService()
            f = getattr(remote, self.goButtonRemoteMethod)
            id = f(self.topPanel.loginPanel.oauthCookie,
                   self.tabName, query, checkWidget)
            if id < 0:
                self.checkResult.add(Label('oops!',
                                           StyleName='userlist-error-title'))
        else:
            self.checkResult.add(Label('Try a non-empty query!',
                                       StyleName='userlist-error-title'))

    def resultsLink(self):
        d = {
        'query' : self.query.getText().strip(),
        'sort' : userlist._sortKey,
        'icon' : userlist._iconSize,
        'tab' : self.tabName,
            }
        
        return '%s?%s' % (defaults.TICKERY_URL, urllib.urlencode(d))

    def adjustSize(self, width, height):
        self.results.adjustSize(width, height)
