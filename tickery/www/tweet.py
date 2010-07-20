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

import server, userlist, text

from pyjamas.ui.HTML import HTML
from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.Grid import Grid
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas import Window
from Popups import DialogBoxModal

POPUP_WIDTH = 600
POPUP_HEIGHT = 275
TWEET_LIMIT = 120

_title = 'Tweet:&nbsp;'
_withAtText = 'With @s'
_withoutAtText = 'No @s'
_doneText = 'link'

_instructions = """Enter your tweet below. A
<a href=\"http://bit.ly\">bit.ly</a> link will automatically
be appended, with a link to your query results. Because the bit.ly link
will occupy 20 characters, you'll need to limit yourself to just 120 below."""


class SimpleTweetPanel(HorizontalPanel):
    def __init__(self, screennames, nUsers, topPanel):
        HorizontalPanel.__init__(self)
        self.screennames = screennames
        self.nUsers = nUsers
        self.topPanel = topPanel
        
        self.add(HTML(_title, StyleName='result-detail'))
        
        self.withButton = Button(_withAtText, self, StyleName='with-at-button')
        self.add(self.withButton)

        self.withoutButton = Button(_withoutAtText, self,
                                    StyleName='without-at-button')
        self.add(self.withoutButton)
        
        self.link = HTML()
        self.add(self.link)

    def onClick(self, sender):
        self.link.setText('')
        if sender == self.withButton:
            self.withButton.setEnabled(False)
            useAts = True
        else:
            self.withoutButton.setEnabled(False)
            useAts = False
        remote = server.TickeryService()
        id = remote.simpleTweet(
            self.topPanel.loginPanel.oauthCookie, self.screennames,
            self.nUsers, userlist._sortKey, useAts, self)
        if id < 0:
            self.link.setText('Oops!')

    def onRemoteResponse(self, response, request_info):
        self.withButton.setEnabled(True)
        self.withoutButton.setEnabled(True)
        if response['result']:
            self.link.setHTML('<a href="%s">%s</a>' %
                              (response['URL'], _doneText))
        else:
            self.link.setText('Oops: %r' % response)

    def onRemoteError(self, code, message, request_info):
        self.withButton.setEnabled(True)
        self.withoutButton.setEnabled(True)
        self.link.setText('Server Err or Invalid Response: ERROR %d - %s' %
                          (code, message))


class TweetEditor(Grid):
    def __init__(self, query, nUsers, tabName, popup, preparePanel, topPanel):
        Grid.__init__(self, 3, 2)
        self.tweet = text.TextAreaFocusHighlight(
            Text="Tickery query %r has %d results. See them at" % (
                query, nUsers),
            VisibleLines=3, MaxLength=1000, StyleName='large-query-area')
        self.tweet.addKeyboardListener(self)
        self.query = query
        self.tabName = tabName
        self.popup = popup
        self.preparePanel = preparePanel
        self.topPanel = topPanel
        self.button = Button('Tweet!', self)
        self.count = Label('')
        
        self.setWidget(0, 0, HTML(_instructions))
        self.setWidget(0, 1, self.count)
        self.setWidget(1, 0, self.tweet)
        self.setWidget(1, 1, self.button)

        formatter = self.getCellFormatter()
        formatter.setVerticalAlignment(0, 1, 'bottom')
        formatter.setVerticalAlignment(1, 1, 'bottom')
        
        self.setCount()

    def onClick(self, sender):
        self.button.setEnabled(False)
        text = self.tweet.getText().strip()
        remote = server.TickeryService()
        id = remote.tweet(
            self.topPanel.loginPanel.oauthCookie, text, self.query,
            self.tabName, userlist._sortKey, self)
        if id < 0:
            self.setWidget(2, 0, Label('Oops!'))

    def onRemoteResponse(self, response, request_info):
        self.button.setEnabled(True)
        if response['result']:
            self.popup.hide()
            self.preparePanel.link.setHTML('<a href="%s"> %s</a>' %
                                           (response['URL'], _doneText))
        else:
            self.setWidget(2, 0, Label('Oops: %r' % response))

    def onRemoteError(self, code, message, request_info):
        self.button.setEnabled(True)
        self.setWidget(2, 0,
                       Label('Server Err or Invalid Response: ERROR %d - %s' %
                             (code, message)))

    def onKeyDown(self, sender, keycode, modifiers):
        pass

    def onKeyUp(self, sender, keycode, modifiers):
        pass

    def onKeyPress(self, sender, keycode, modifiers):
        self.setCount()

    def setCount(self):
        n = TWEET_LIMIT - len(self.tweet.getText())
        if n >= 0:
            self.count.setStyleName('tweet-char-count-ok')
        else:
            self.count.setStyleName('tweet-char-count-excessive')
        self.count.setText(str(n))
        
        
class TweetPopup(DialogBoxModal):
    def __init__(self, identifier, query, nUsers, tabName,
                 preparePanel, topPanel):
        DialogBoxModal.__init__(self, identifier, autoHide=True)
        self.setWidth('%dpx' % POPUP_WIDTH)
        self.setHeight('%dpx' % POPUP_HEIGHT)
        self.setWidget(
            TweetEditor(query, nUsers, tabName, self, preparePanel, topPanel))

    def onClick(self, sender):
        self.hide()


class PrepareTweetButton(HorizontalPanel):
    def __init__(self, query, nUsers, tabName, topPanel):
        HorizontalPanel.__init__(self)
        self.button = Button('Compose tweet', self,
                             StyleName='compose-tweet-button')
        self.add(self.button)        
        self.link = HTML()
        self.add(self.link)
        self.popup = TweetPopup(self.__class__.__name__,
                                query, nUsers, tabName, self, topPanel)
        self.popup.setText('Compose a tweet')

    def onClick(self, sender):
        width = (Window.getClientWidth() - POPUP_WIDTH) / 2.0
        self.popup.setPopupPosition(width, 100)
        self.popup.show()
