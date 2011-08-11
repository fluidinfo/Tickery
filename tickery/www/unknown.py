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
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Grid import Grid
from pyjamas.ui.VerticalPanel import VerticalPanel

import utils
import go


class UserList(VerticalPanel):
    def __init__(self, names):
        VerticalPanel.__init__(self, Spacing=8, StyleName='userlist-error-box')
        self.add(Label(self.msg, StyleName='userlist-error-title'))
        s = []
        for name in names:
            if self.link:
                s.append(utils.screennameToTwitterLink(name))
            else:
                s.append(name)
        self.add(HTML('<br/>'.join(s), StyleName='userlist-error-text'))


class NonexistentUsers(UserList):
    link = False
    msg = "We can't run your query because the following users " \
          "do not seem to exist on Twitter:"


class ProtectedUsers(UserList):
    link = True
    msg = "We can't run your query because the following users have " \
          "their details protected on Twitter:"


class OtherErrorUsers(UserList):
    link = True
    msg = "Sorry, we ran into a problem trying to handle the following users:"


class TooManyFriends(VerticalPanel):
    def __init__(self, names, limit):
        VerticalPanel.__init__(self, Spacing=8, StyleName='userlist-error-box')
        self.add(Label(
            "The following people have too many friends! The current "
            "supported limit is %s." % utils.splitthousands(limit),
            StyleName='userlist-error-title'))
        s = []
        for name, friends in names:
            n = utils.splitthousands(friends)
            s.append('%s (%s friends)' % (
                utils.screennameToTwitterLink(name),
                utils.screennameToTwitterFriendsLink(name, n)))
        self.add(HTML('<br/>'.join(s), StyleName='userlist-error-text'))


class TooManyResults(Label):
    def __init__(self, n, limit):
        Label.__init__(self,
            "Sorry, your query had too many (%s) results! The current "
            "supported limit is %s." % (
                           utils.splitthousands(n),
                           utils.splitthousands(limit)),
            StyleName='userlist-error-title')


class UnaddedUsers(VerticalPanel):
    def __init__(self, statusSummary, sender):
        VerticalPanel.__init__(self, Spacing=10,
                               StyleName='userlist-error-box')
        self.add(HTML("We're currently working on users you mentioned",
                      StyleName='userlist-error-title'))

        self.add(HTML(
            """<p>Below is a summary of work already in progress, or
        queued, which must complete before we can run your query. Please
        note that Tickery is subject to Twitter's API rate limiting and
        general network latency, so you may need to be patient. We'll get
        there!</p>

        <p><a href=\"%s\">Here's a link</a> to this results page so you can
        come back to see how we're doing.  You can also click %r again to
        see updated progress.</p>""" %
            (sender.resultsLink(), go.goButtonText),
            StyleName='userlist-error-text'))

        nRows = 0

        underway = statusSummary['underway']
        nUnderway = len(underway)
        queued = statusSummary['queued']
        nQueued = len(queued)

        nCols = 4
        width = 200

        if nUnderway:
            nRows += nUnderway + 1
        if nQueued:
            nRows += nQueued + 1

        g = Grid(nRows, nCols, StyleName='users')
        g.setCellPadding(2)
        cellFormatter = g.getCellFormatter()
        row = 0

        if nUnderway:
            g.setHTML(row, 0, 'Users currently being processed&nbsp;')
            cellFormatter.setStyleName(row, 0, 'title-lhs')
            g.setText(row, 1, 'Name')
            cellFormatter.setStyleName(row, 1, 'title')
            g.setText(row, 2, 'Friends')
            cellFormatter.setStyleName(row, 2, 'title')
            g.setText(row, 3, '% done')
            cellFormatter.setStyleName(row, 3, 'title')
            cellFormatter.setWidth(row, 3, width)
            row += 1

            for u, nFriends, done in underway:
                cellFormatter.setStyleName(row, 0, 'blank')
                n = utils.splitthousands(nFriends)
                g.setHTML(row, 1, utils.screennameToTwitterLink(u))
                g.setHTML(row, 2, utils.screennameToTwitterFriendsLink(u, n))
                cellFormatter.setHorizontalAlignment(row, 2, 'right')

                pct = '%d' % int(done * 100.0)
                left = Label(pct, StyleName='done', Width=int(done * width))
                g.setWidget(row, 3, left)

                row += 1

        if nQueued:
            g.setHTML(row, 0, 'Users queued for processing&nbsp;')
            cellFormatter.setStyleName(row, 0, 'title-lhs')
            g.setText(row, 1, 'Name')
            cellFormatter.setStyleName(row, 1, 'title')
            g.setText(row, 2, 'Friends')
            cellFormatter.setStyleName(row, 2, 'title')
            g.setText(row, 3, 'Queue position')
            cellFormatter.setStyleName(row, 3, 'title')
            row += 1

            for u, nFriends, pos in queued:
                cellFormatter.setStyleName(row, 0, 'blank')
                n = utils.splitthousands(nFriends)
                g.setHTML(row, 1, utils.screennameToTwitterLink(u))
                g.setHTML(row, 2, utils.screennameToTwitterFriendsLink(u, n))
                cellFormatter.setHorizontalAlignment(row, 2, 'right')
                g.setText(row, 3, pos)
                cellFormatter.setHorizontalAlignment(row, 3, 'right')
                row += 1

        self.add(g)
