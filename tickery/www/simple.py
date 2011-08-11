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
import utils
import userlist
import go
import server
import text
import defaults
from results import ResultHandler

from tickerytab import TickeryTab

from pyjamas.ui.HTML import HTML
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui import KeyboardListener
from pyjamas.ui.Label import Label
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas import DOM, Window

_defaultName1 = 'timoreilly'
_defaultName2 = 'timbray'


class Simple(TickeryTab):

    tabName = 'simple'
    textBoxLength = 18

    def __init__(self, topPanel):
        TickeryTab.__init__(self, topPanel)
        # Get query names (if they exist) from the request. We don't check
        # that we're the wanted tab: if 2 names are given, just use them.
        args = Window.getLocation().getSearchDict()
        name1 = args.get('name1')
        name2 = args.get('name2')

        if name1 and name2:
            self.autoActivate = True

        if name1:
            name1 = urllib.unquote_plus(name1)
        else:
            name1 = _defaultName1

        if name2:
            name2 = urllib.unquote_plus(name2)
        else:
            name2 = _defaultName2

        v1 = VerticalPanel()
        self.name1 = text.TextBoxFocusHighlight(
            Text=name1, MaxLength=self.textBoxLength,
            VisibleLength=self.textBoxLength, StyleName='simple-query-box')
        v1.add(self.name1)
        self.followResult1 = HorizontalPanel(Spacing=4)
        v1.add(self.followResult1)

        v2 = VerticalPanel()
        self.name2 = text.TextBoxFocusHighlight(
            Text=name2, MaxLength=self.textBoxLength,
            VisibleLength=self.textBoxLength, StyleName='simple-query-box')
        v2.add(self.name2)
        self.followResult2 = HorizontalPanel(Spacing=4)
        v2.add(self.followResult2)

        self.goButton = go.GoButton(self)

        v = VerticalPanel(Spacing=2, StyleName='help-panel')
        v.add(HTML('Enter two Twitter usernames',
                   StyleName='simple-instructions'))
        v.add(v1)
        h = HorizontalPanel()
        h.add(v2)
        h.add(self.goButton)
        v.add(h)

        self.topGrid.setWidget(0, 1, v)
        formatter = self.topGrid.getCellFormatter()
        formatter.setHorizontalAlignment(0, 1, 'left')

        self.checkResult = HorizontalPanel()
        self.add(self.checkResult)

        self.results = userlist.UserListPanel(self, topPanel)
        self.add(self.results)

        # allow keypress ENTER reaction
        self.name1.addKeyboardListener(self)
        self.name2.addKeyboardListener(self)

    def setInputFocus(self):
        self.name1.setFocus(True)

    def clearResults(self):
        self.results.clear()

    def onKeyDown(self, sender, keycode, modifiers):
        pass

    def onKeyUp(self, sender, keycode, modifiers):
        pass

    def onKeyPress(self, sender, keycode, modifiers):
        enter = keycode == KeyboardListener.KEY_ENTER
        enterOrTab = enter or keycode == KeyboardListener.KEY_TAB

        if sender == self.name1:
            if enterOrTab:
                # Move to name2 & highlight.
                DOM.eventPreventDefault(DOM.eventGetCurrentEvent())
                self.name2.setFocus(True)
                self.name2.highlight()
        elif sender == self.name2:
            if enter:
                if modifiers & KeyboardListener.MODIFIER_SHIFT:
                    # Move back to name1 & highlight.
                    self.name1.setFocus(True)
                    self.name1.highlight()
                else:
                    # Send query.
                    DOM.eventPreventDefault(DOM.eventGetCurrentEvent())
                    self.process()

    def onClick(self, sender):
        self.process()

    def getNames(self):
        name1 = self.name1.getText().strip()
        if name1.startswith('@'):
            name1 = name1[1:].lstrip()
        name2 = self.name2.getText().strip()
        if name2.startswith('@'):
            name2 = name2[1:].lstrip()
        return [name1, name2]

    def process(self):
        self.checkResult.clear()
        self.followResult1.clear()
        self.followResult2.clear()
        name1, name2 = self.getNames()
        if not name1 or not name2:
            self.checkResult.add(Label('Please enter two Twitter user names!',
                                       StyleName='userlist-error-title'))
        elif name1 == name2:
            self.checkResult.add(Label(
                "Let's try that again, with names that are not the same.",
                StyleName='userlist-error-title'))
        elif name1.find(' ') != -1 or name2.find(' ') != -1:
            self.checkResult.add(Label(
                'User names cannot contain spaces.',
                StyleName='userlist-error-title'))
        else:
            query = '%s and %s' % (name1, name2)
            self.goButton.setEnabled(False)
            followLabelAdder = AddFollowLabels(self)
            callbackFunc = getattr(followLabelAdder, 'process')
            titleMaker = TitleMaker(name1, name2)
            titleFunc = getattr(titleMaker, 'makeTitle')
            handler = ResultHandler(query, self, self.tabName,
                                    titleFunc, callback=callbackFunc)
            remote = server.TickeryService()
            id = remote.intermediateQuery(self.topPanel.loginPanel.oauthCookie,
                                          self.tabName, query, handler)
            if id < 0:
                self.results.add(Label('oops!'))

    def resultsLink(self):
        name1, name2 = self.getNames()
        d = {
        'name1': name1,
        'name2': name2,
        'sort': userlist._sortKey,
        'icon': userlist._iconSize,
        'tab': self.tabName,
            }

        return '%s?%s' % (defaults.TICKERY_URL, urllib.urlencode(d))

    def adjustSize(self, width, height):
        self.results.adjustSize(width, height)


class FriendOf(object):
    def __init__(self, name, panel, sender):
        self.name = name
        self.panel = panel
        self.sender = sender

    def onRemoteResponse(self, follows, request_info):
        if follows:
            f = 'follows'
        else:
            f = "doesn't follow"
        self.panel.add(
            HTML('%s %s' % (f, utils.screennameToTwitterLink(self.name)),
                 StyleName='follow-result'))

    def onRemoteError(self, code, message, request_info):
        self.sender.results.add(Label(
            'Status: Server Err or Invalid Response: %s (code %d)' %
            (message, code)))


class AddFollowLabels(object):
    def __init__(self, sender):
        self.sender = sender

    def process(self):
        name1, name2 = self.sender.getNames()
        remote = server.TickeryService()
        friendWidget = FriendOf(name2, self.sender.followResult1, self.sender)
        id = remote.friendOf(name1, name2, friendWidget)
        if id < 0:
            self.sender.results.add(Label('oops!'))
        friendWidget = FriendOf(name1, self.sender.followResult2, self.sender)
        id = remote.friendOf(name2, name1, friendWidget)
        if id < 0:
            self.sender.results.add(Label('oops!'))


class TitleMaker(object):
    def __init__(self, name1, name2):
        self.name1 = name1
        self.name2 = name2

    def makeTitle(self, users):
        if users:
            nUsers = len(users)
            if nUsers > 1:
                what = 'people'
            else:
                what = 'person'
            return '%s and %s follow %s %s in common:' % (
                self.name1, self.name2, nUsers, what)
        else:
            return "%s and %s don't follow anyone in common!" % (
                self.name1, self.name2)
