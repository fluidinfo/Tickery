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

import defaults
import server
import tickerytab
import utils

from pyjamas.ui.Grid import Grid
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Image import Image
from pyjamas.ui.Button import Button
from pyjamas.ui.Label import Label
from pyjamas.ui import HasAlignment, Event
from pyjamas import Window, Cookies, DOM


def _deleteCookie():
    # Set the cookie back in time a few years.
    Cookies.setCookie(defaults.OAUTH_COOKIE, '', -100000000)

WHY_BUTTON_TEXT = 'why?'
WHY_TITLE = 'Why sign in with Twitter?'
WHY_TEXT = """
Tickery has several useful features that are only available when you're
signed in to Twitter. You'll be able to:

<ul>
<li>Filter search results by who you're following / not following.</li>
<li>Follow / unfollow Twitter users in Tickery search results.</li>
<li>Send tweets containing links to Tickery search results.</li>
</ul>

The <img src=\"login.png\"> button will take you to Twitter, where you can
authorize Tickery to interact with Twitter on your behalf. Tickery never
has access to your Twitter password.

</p>

<p>

After authorizing Tickery, you'll automatically be redirected back here.
Your Tickery results will then display extra buttons and menus.

</p>

"""


class LoginPanel(Grid):
    def __init__(self):
        Grid.__init__(self, 1, 2, StyleName='login-panel')
        self.setCellPadding(0)
        self.setCellSpacing(0)
        formatter = self.getCellFormatter()
        # formatter.setWidth(0, 0, '100%')
        formatter.setHorizontalAlignment(0, 0, 'right')
        formatter.setHorizontalAlignment(0, 1, 'right')
        self.loggedIn = False
        self.screenname = None
        self.friendsIds = None
        self.userListPanels = []
        self.oauthCookie = Cookies.getCookie(defaults.OAUTH_COOKIE)
        if self.oauthCookie:
            remote = server.TickeryService()
            id = remote.screenameFromCookie(self.oauthCookie,
                                            DisplayLoggedIn(self))
            if id < 0:
                self.setWidget(0, 1, Label('oops: getScreenameFromCookie'))
        else:
            self.notLoggedIn()

    def notLoggedIn(self):
        if self.oauthCookie:
            _deleteCookie()
            self.oauthCookie = None
        self.clear()
        self.loggedIn = False
        self.screenname = None
        self.friendsIds = None
        loginImage = Image('login.png', StyleName='login-image')
        loginImage.addMouseListener(self)
        self.setWidget(0, 0, loginImage)
        why = Button(WHY_BUTTON_TEXT, self, StyleName='why-button')
        self.setWidget(0, 1, why)
        self.instructions = HTML(WHY_TEXT,
                                 StyleName='instructions-popup',
                                 HorizontalAlignment=HasAlignment.ALIGN_LEFT)
        self.popup = tickerytab.InstructionBox(
            self.__class__.__name__, self.instructions)
        self.popup.setText(WHY_TITLE)

    def addUserListPanel(self, panel):
        self.userListPanels.append(panel)

    def onMouseEnter(self, sender):
        pass

    def onMouseMove(self, sender, x, y):
        pass

    def onMouseLeave(self, sender):
        pass

    def onMouseDown(self, sender, x, y):
        pass

    def onMouseUp(self, sender, x, y):
        event = DOM.eventGetCurrentEvent()
        eventButton = DOM.eventGetButton(event)
        if eventButton == Event.BUTTON_LEFT:
            remote = server.TickeryService()
            id = remote.login(LoginRedirector(self))
            if id < 0:
                self.setWidget(0, 1, Label('oops: LoginPanel'))

    def onClick(self, sender):
        width = (Window.getClientWidth() - tickerytab.POPUP_WIDTH) / 2.0
        self.popup.setPopupPosition(width, 100)
        self.popup.show()


class LoginRedirector(object):
    def __init__(self, sender):
        self.sender = sender

    def onRemoteResponse(self, result, request_info):
        if result['result']:
            URL = result['URL']
            Window.setLocation(URL)
        else:
            self.sender.setWidget(
                0, 1, Label('Could not get login redirect URL: ' +
                            result['error']))

    def onRemoteError(self, code, message, request_info):
        self.sender.setWidget(
            0, 1, Label('Could not get login redirect URL: ' + message))


class DisplayLoggedIn(object):
    def __init__(self, sender):
        self.sender = sender

    def onRemoteResponse(self, result, request_info):
        if result['result']:
            self.sender.screenname = screenname = result['screen_name']
            h = HTML('%s&nbsp;' % utils.screennameToTwitterLink(screenname),
                     StyleName='logged-in-text')
            self.sender.setWidget(0, 0, h)
            logout = Image('logout.gif', StyleName='logout-image')
            logout.addMouseListener(self)
            self.sender.setWidget(0, 1, logout)
            remote = server.TickeryService()
            id = remote.friendsIds(self.sender.oauthCookie,
                screenname, SetFriends(screenname, self.sender))
            if id < 0:
                self.sender.setWidget(
                    0, 1, Label("Oops: Couldn't fetch friends."))
        else:
            self.sender.notLoggedIn()

    def onRemoteError(self, code, message, request_info):
        self.sender.notLoggedIn()

    def onMouseEnter(self, sender):
        pass

    def onMouseMove(self, sender, x, y):
        pass

    def onMouseLeave(self, sender):
        pass

    def onMouseDown(self, sender, x, y):
        pass

    def onMouseUp(self, sender, x, y):
        event = DOM.eventGetCurrentEvent()
        eventButton = DOM.eventGetButton(event)
        if eventButton == Event.BUTTON_LEFT:
            _deleteCookie()
            remote = server.TickeryService()
            id = remote.logout(self.sender.oauthCookie,
                               LogoutRedirector(self.sender))
            if id < 0:
                self.sender.setWidget(
                    0, 1, Label("Oops: Couldn't call log out!"))


class LogoutRedirector(object):
    def __init__(self, sender):
        self.sender = sender

    def onRemoteResponse(self, result, request_info):
        self.sender.notLoggedIn()

    def onRemoteError(self, code, message, request_info):
        self.sender.notLoggedIn()


class SetFriends(object):
    def __init__(self, screenname, sender):
        self.screenname = screenname
        self.sender = sender

    def onRemoteResponse(self, result, request_info):
        friendsIds = result['friendsIds']
        d = {}
        for fid in friendsIds:
            d[fid] = None
        # TODO: figure out if the next line is right or an accidental
        # insertion of " #" that just happens to have created valid
        # code. The "d #ict" code is running on tickery.net
        self.sender.friendsIds = d  # ict.fromkeys(friendsIds)
        self.sender.loggedIn = True
        # All done, finalize the setup of all existing UserListPanels so
        # they can filter users based on the friendsIds we just retrieved.
        for userListPanel in self.sender.userListPanels:
            userListPanel.addFilterWidgets()

    def onRemoteError(self, code, message, request_info):
        self.sender.setWidget(
            0, 1, Label("Could not retrieve friends: %s" % message))
