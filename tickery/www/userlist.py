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

import utils, tweet, server, defaults

from pyjamas.ui.Label import Label
from pyjamas.ui.Image import Image
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Button import Button
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.FlowPanel import FlowPanel
from pyjamas import Timer, Window

_followText = 'Follow'
_unfollowText = 'Unfollow'

_iconSize = 'medium'
_iconData = (('Small', 'small'),
             ('Medium', 'medium'),
             ('Large', 'large'),
             )

def setIconSize(size):
    global _iconSize
    if size and size in [d[1] for d in _iconData]:
        _iconSize = size

# These look nice in FF, but don't work in MSIE:
# _up = u'\N{NORTH EAST ARROW}'
# _dn = u'\N{SOUTH EAST ARROW}'

# These work in FF, but partly work on Mac OS X & don't work in some MSIE:
_up = u'\N{WHITE UP-POINTING TRIANGLE}'
_dn = u'\N{WHITE DOWN-POINTING TRIANGLE}'

_sortKey = 'screen_name'
_sortKeyData = ((u'@Name ' + _up, 'screen_name'),
                (u'Name ' + _up, 'name'),
                (u'# Friends ' + _dn, 'friends_count'),
                (u'# Followers ' + _dn, 'followers_count'),
                (u'# Tweets ' + _dn, 'statuses_count'),
                (u'Twitter id ' + _up, 'id'),
                (u'Location ' + _up, 'location'),
                (u'Public (true/false)', 'protected'),
                )

def setSortKey(key):
    global _sortKey
    if key and key in [d[1] for d in _sortKeyData]:
        _sortKey = key
        

class LargeAvatar(VerticalPanel):
    def __init__(self, userListPanel, tabPanel, topPanel):
        VerticalPanel.__init__(self, StyleName='large-avatar-panel')
        self.userListPanel = userListPanel
        self.tabPanel = tabPanel
        self.topPanel = topPanel
        upperPanel = HorizontalPanel(StyleName='large-avatar-upper-panel',
                                     Spacing=8)
        self.image = Image(StyleName='large-avatar')
        self.upperText = HTML(StyleName='large-avatar-upper-text')
        upperPanel.add(self.image)
        upperPanel.add(self.upperText)
        self.add(upperPanel)
        self.lowerText = HTML(StyleName='large-avatar-lower-text')
        self.add(self.lowerText)
        self.followButton = None
        self.user = None
        insertPanel = HorizontalPanel(Spacing=3)
        insertPanel.add(Label('Use name: '))
        if tabPanel.tabName == 'simple':
            b1 = Button('upper', SimpleInserter(self, 'upper'))
            b2 = Button('lower', SimpleInserter(self, 'lower'))
            insertPanel.add(b1)
            insertPanel.add(b2)
        else:
            b1 = Button('or', QueryInserter(self, 'or'))
            b2 = Button('and', QueryInserter(self, 'and'))
            b3 = Button('except', QueryInserter(self, 'except'))
            insertPanel.add(b1)
            insertPanel.add(b2)
            insertPanel.add(b3)
        self.add(insertPanel)

    def setUser(self, u):
        self.user = u
        screenname = u['screen_name']
        self.image.setUrl(u['profile_image_url'])
        self.upperText.setHTML(
            '''%s<br/>%s''' %
            (u['name'],
             utils.screennameToTwitterLink(screenname, '@' + screenname)))
        
        friends = utils.splitthousands(u['friends_count'])
        followers = utils.splitthousands(u['followers_count'])
        tweets = utils.splitthousands(u['statuses_count'])
        location = u['location'] or 'unknown'
        self.lowerText.setHTML(
            '''Friends:&nbsp;%s<br/>
               Followers:&nbsp;%s<br/>
               Tweets:&nbsp;%s<br/>
               Location:&nbsp;%s<br/>
               Twitter id:&nbsp;%s<br/>
               Private:&nbsp;%s''' %
            (utils.screennameToTwitterFriendsLink(screenname, friends),
             utils.screennameToTwitterFollowersLink(screenname, followers),
             utils.screennameToTwitterLink(screenname, tweets),
             location, utils.splitthousands(u['id']), u['protected']))

        if self.followButton:
            self.remove(self.followButton)
            self.followButton = None
            
        following = u.get('following')
        if following is not None:
            if self.topPanel.loginPanel.screenname == screenname:
                # OK, I admit, this is ugly.
                self.followButton = Label("That's you!",
                                          StyleName='follow-button')
            else:
                if following:
                    text = _unfollowText
                else:
                    text = _followText
                self.followButton = Button(text, self,
                                           StyleName='follow-button')
            self.add(self.followButton)

    def onClick(self, sender):
        self.followButton.setEnabled(False)
        cookie = self.topPanel.loginPanel.oauthCookie
        remote = server.TickeryService()
        if self.user['following']:
            func = remote.unfollow
        else:
            func = remote.follow
        id = func(cookie, self.user['id'],
                  UpdateFollow(self, self.userListPanel, self.topPanel))
        if id < 0:
            self.add(Label('oops: could not call follow/unfollow'))


class SimpleInserter(object):
    def __init__(self, largeAvatar, side):
        self.largeAvatar = largeAvatar
        self.side = side

    def onClick(self, sender):
        if self.side == 'upper':
            dest = self.largeAvatar.tabPanel.name1
        else:
            dest = self.largeAvatar.tabPanel.name2
        name = self.largeAvatar.user['screen_name']
        dest.setText(name)
        dest.setCursorPos(len(name))


class QueryInserter(object):
    def __init__(self, largeAvatar, op):
        self.largeAvatar = largeAvatar
        self.op = op

    def onClick(self, sender):
        name = self.largeAvatar.user['screen_name']
        dest = self.largeAvatar.tabPanel.query
        pos = dest.getCursorPos()
        text = dest.getText()
        if self.largeAvatar.tabPanel.tabName == 'advanced':
            name = 'has %s/%s/%s' % (defaults.TWITTER_USERNAME,
                                     defaults.TWITTER_FRIENDS_NAMESPACE_NAME,
                                     name)
        if pos == 0:
            preOp = ''
            if len(text):
                postOp = ' ' + self.op
            else:
                postOp = ''
        else:
            preOp = self.op + ' '
            postOp = ''

        if pos and text[pos - 1] != ' ':
            initialSpace = ' '
        else:
            initialSpace = ''

        if len(text) > pos and text[pos] != ' ':
            finalSpace = ' '
        else:
            finalSpace = ''

        insert = '%s%s%s%s%s' % (initialSpace, preOp, name, postOp, finalSpace)
        new = '%s%s%s' % (text[0:pos], insert, text[pos:])
        dest.setText(new)
        dest.setCursorPos(pos + len(insert))


class UpdateFollow(object):
    def __init__(self, largeAvatar, userListPanel, topPanel):
        self.largeAvatar = largeAvatar
        self.userListPanel = userListPanel
        self.topPanel = topPanel

    def onRemoteResponse(self, result, request_info):
        user = self.largeAvatar.user
        followButton = self.largeAvatar.followButton
        user['following'] = not user['following']
        if user['following']:
            followButton.setText(_unfollowText)
            self.userListPanel.filterChanger.follow(user)
        else:
            followButton.setText(_followText)
            self.userListPanel.filterChanger.unfollow(user)
        followButton.setEnabled(True)

    def onRemoteError(self, code, message, request_info):
        self.largeAvatar.followButton.setEnabled(True)
        self.largeAvatar.add(Label('Could not follow/unfollow: ' + message))
        

class UserListPanel(VerticalPanel):
    def __init__(self, tabPanel, topPanel, **kwargs):
        VerticalPanel.__init__(self, StyleName='user-list-panel', **kwargs)
        self.tabPanel = tabPanel
        self.topPanel = topPanel
        self.iconAdder = None
        self.iconPanel = None
        self.nSelected = 0
        self.leftPanelWidth = 340
        self.widthFudgeFactor = 25

    def clear(self):
        VerticalPanel.clear(self)
        self.nSelected = 0

    def updateResultLink(self):
        self.resultLink.setHTML('Results:&nbsp;<a href="%s">link</a>' %
                                self.tabPanel.resultsLink())
    
    def setUsers(self, title, users, kwargs):
        self.users = users
        self.nUsers = len(users)
        self.title = title
        self.resultPanel = HorizontalPanel(StyleName='result-panel')
        self.add(self.resultPanel)
        self.leftPanel = VerticalPanel(StyleName='results-left-panel',
                                       Width=self.leftPanelWidth)
        self.resultPanel.add(self.leftPanel)
        if not users:
            self.iconPanel = None
            self.leftPanel.add(HTML(title, StyleName='result-title'))
        else:
            # Set a display order that will show everything for now.
            self.displayOrder = range(self.nUsers)
            self.largeAvatar = LargeAvatar(self, self.tabPanel, self.topPanel)
            self.leftPanel.add(self.largeAvatar)

            resultPanelBottomLeft = VerticalPanel(
                StyleName='results-left-panel-bottom-left')

            self.resultLink = HTML(StyleName='result-detail')
            self.updateResultLink()
            resultPanelBottomLeft.add(self.resultLink)
            
            self.iconSizePanel = HorizontalPanel()
            self.iconSizePanel.add(
                HTML('Icons:&nbsp;', StyleName='result-detail'))

            self.iconSizeLb = lb = ListBox()
            i = 0
            for text, key in _iconData:
                lb.addItem(text, key)
                if key == _iconSize:
                    lb.setSelectedIndex(i)
                i += 1
            lb.addChangeListener(IconSizeChanger(self))
            self.iconSizePanel.add(lb)
            resultPanelBottomLeft.add(self.iconSizePanel)

            if self.nUsers > 1:
                self.sortPanel = HorizontalPanel()
                self.sortPanel.add(
                    HTML('Sort:&nbsp;', StyleName='result-detail'))

                self.lb = lb = ListBox()
                i = 0
                for text, key in _sortKeyData:
                    lb.addItem(text, key)
                    if key == _sortKey:
                        lb.setSelectedIndex(i)
                    i += 1
                lb.addChangeListener(self)
                self.sortPanel.add(lb)
                resultPanelBottomLeft.add(self.sortPanel)
                
            self.filterPanel = HorizontalPanel()
            resultPanelBottomLeft.add(self.filterPanel)
            self.addFilterWidgets()
            
            if self.topPanel.loggedIn():
                if 'screennames' in kwargs:
                    resultPanelBottomLeft.add(tweet.SimpleTweetPanel(
                        kwargs['screennames'], len(self.users), self.topPanel))
                elif 'query' in kwargs:
                    resultPanelBottomLeft.add(tweet.PrepareTweetButton(
                        kwargs['query'], len(self.users),
                        self.tabPanel.tabName, self.topPanel))

            self.leftPanel.add(resultPanelBottomLeft)

            self.iconPanel = VerticalPanel(StyleName='icon-outer-panel')
            self.resultPanel.add(self.iconPanel)
            self.images = []
            for u in users:
                url = u['profile_image_url']
                i = Image(url, StyleName='avatar-' + _iconSize)
                # Does calling prefetch actually help?
                i.prefetch(url)
                i._user = u
                i._selected = False
                i.addMouseListener(self)
                self.images.append(i)
            self.showUsers()

    def addFilterWidgets(self):
        """If we're logged in (and hence the friends list is available),
        create a filter listbox. If not, tell the loginPanel that we exist
        so it can call us when the login is complete."""
        if self.topPanel.loggedIn():
            # Window.alert('Logged in')
            self.filterPanel.add(
                HTML('Filter:&nbsp;', StyleName='result-detail'))
            self.filterChanger = FilterChanger(self, self.topPanel)
            self.filterBox = ListBox()
            self.filterBox.addItem('None', 0)
            self.filterBox.addItem(
                'Following (%d of %d)' %
                (self.filterChanger.nFriends, self.nUsers), 1)
            self.filterBox.addItem(
                "Not following (%d of %d)" %
                (self.nUsers - self.filterChanger.nFriends, self.nUsers), 2)
            self.filterBox.addChangeListener(self.filterChanger)
            self.filterPanel.add(self.filterBox)
        else:
            # Not yet logged in. Add ourselves to the list of UserListPanels
            # that the loginPanel will call when it's ready.
            self.topPanel.loginPanel.addUserListPanel(self)
                    
    def onChange(self, sender):
        global _sortKey
        _sortKey = self.lb.getValue(self.lb.getSelectedIndex())
        self.updateResultLink()
        self.showUsers()

    def showUsers(self):
        # Cancel any existing timed icon additions before changing
        # self.displayOrder.
        if self.iconAdder is not None:
            self.iconAdder.cancel()
            self.iconAdder = None
            
        self.iconPanel.clear()

        # Set a title above the icons.
        if hasattr(self, 'filterChanger'):
            order = self.filterChanger.currentOrder
            if order == 0:
                title = self.title
            else:
                if order == 1:
                    n = self.filterChanger.nFriends
                    detail = 'follow'
                else:
                    n = self.nUsers - self.filterChanger.nFriends
                    detail = "don't follow"
                if n == 0:
                    if detail == 'follow':
                        title = "You don't follow any of them!"
                    else:
                        title = "You already follow them all!"
                else:
                    if n > 1:
                        plural = 's'
                    else:
                        plural = ''
                    title = 'The %d user%s you %s:' % (n, plural, detail)
        else:
            title = self.title
        self.iconPanel.add(HTML(title, StyleName='result-title'))
        
        if not self.displayOrder:
            # There are no users to show.
            return
            
        decreasing = _sortKey in (
            'friends_count', 'followers_count', 'statuses_count')
        alpha = _sortKey in ('screen_name', 'name', 'location')
        def _keyFunc(n):
            value = self.users[n][_sortKey]
            if decreasing:
                return -1 * value
            elif alpha:
                if value:
                    return value.lower().strip()
                else:
                    # Uh, put this towards the end (of ASCII at least)
                    return '~~~'
            else:
                return value

        # Don't use sorted here, as it replaces the display order list
        # (which is actually being maintained for us by our FilterChanger
        # instance).
        self.displayOrder.sort(key=_keyFunc)
        self.icons = FlowPanel(StyleName='icon-panel')
        self.adjustWidths()
        self.iconPanel.add(self.icons)
        self.iconAdder = IconAdder(self)
        Timer.Timer(1, self.iconAdder)
        if self.nSelected == 0:
            self.largeAvatar.setUser(self.users[self.displayOrder[0]])

    def onMouseEnter(self, img):
        if not self.nSelected:
            self.largeAvatar.setUser(img._user)

    def onMouseMove(self, img, x, y):
        pass

    def onMouseLeave(self, img):
        pass

    def onMouseDown(self, img, x, y):
        self.largeAvatar.setUser(img._user)
        if not img._selected and self.nSelected:
            self._unselectAll()
        self._toggleSelect(img)

    def onMouseUp(self, img, x, y):
        pass

    def _toggleSelect(self, img):
        if img._selected:
            self._unselect(img)
        else:
            self._select(img)
        
    def _unselect(self, img):
        if img._selected:
            img.removeStyleDependentName('selected')
            self.nSelected -= 1
            img._selected = False

    def _select(self, img):
        if not img._selected:
            img.addStyleDependentName('selected')
            self.nSelected += 1
            img._selected = True

    def _unselectAll(self):
        for img in self.images:
            self._unselect(img)

    def unselectNotFollowed(self):
        for img in self.images:
            if not img._user['following'] and img._selected:
                self._unselect(img)

    def unselectFollowed(self):
        for img in self.images:
            if img._user['following'] and img._selected:
                self._unselect(img)

    def setIconSizes(self):
        for img in self.images:
            selected = img._selected
            if selected:
                self._unselect(img)
            img.setStyleName('avatar-' + _iconSize)
            if selected:
                self._select(img)

    def adjustWidths(self, windowWidth=None):
        if windowWidth is None:
            windowWidth = Window.getClientWidth()
        width = windowWidth - self.leftPanelWidth - self.widthFudgeFactor
        if self.iconPanel is not None:
            self.icons.setWidth(width)

    def adjustSize(self, width, height):
        self.adjustWidths(width)

class IconAdder(object):

    _updatesPerLoop = 5
    
    def __init__(self, userListPanel):
        self.userListPanel = userListPanel
        self.index = 0
        self.cancelled = False
        self.nUsers = len(userListPanel.displayOrder)
        
    def onTimer(self, sender):
        imagesAndIds = self.userListPanel.images
        displayOrder = self.userListPanel.displayOrder
        iconAdd = self.userListPanel.icons
        for count in range(self._updatesPerLoop):
            if self.cancelled or self.index == self.nUsers:
                return
            iconAdd.add(imagesAndIds[displayOrder[self.index]])
            self.index += 1
        Timer.Timer(1, self)

    def cancel(self):
        self.cancelled = True


class FilterChanger(object):
    def __init__(self, userListPanel, topPanel):
        self.userListPanel = userListPanel
        self.currentOrder = 0
        friendsIds = topPanel.loginPanel.friendsIds
        following = []
        notFollowing = []
        i = 0
        for user in userListPanel.users:
            if user['id'] in friendsIds:
                following.append(i)
                user['following'] = True
            else:
                notFollowing.append(i)
                user['following'] = False
            i += 1
        self.orders = [range(userListPanel.nUsers), following, notFollowing]
        self.nFriends = len(following)

    def onChange(self, filterBox):
        order = filterBox.getValue(filterBox.getSelectedIndex())
        self.currentOrder = order
        self.userListPanel.displayOrder = self.orders[order]
        if order == 1:
            self.userListPanel.unselectNotFollowed()
        elif order == 2:
            self.userListPanel.unselectFollowed()
        self.userListPanel.showUsers()

    def _updateFilterButtonText(self):
        setItemText = self.userListPanel.filterBox.setItemText
        n = self.userListPanel.nUsers
        setItemText(1, "Following (%d of %d)" % (self.nFriends, n))
        setItemText(2, "Not following (%d of %d)" % (n - self.nFriends, n))

    def follow(self, user):
        # Move the user from the unfollowing list to the following list.
        # Window.alert('In follow: %r' % (user,))
        wantedId = user['id']
        users = self.userListPanel.users
        # Linear search, FTW!
        for index in self.orders[2]:
            if users[index]['id'] == wantedId:
                # Linear search again!
                self.orders[2].remove(index)
                self.orders[1].append(index)
                self.nFriends += 1
                if self.currentOrder != 0:
                    # Only redisplay if we're not looking at the full list.
                    self.userListPanel.showUsers()
                self._updateFilterButtonText()
                break

    def unfollow(self, user):
        # Move the user from the following list to the unfollowing list.
        # Window.alert('In unfollow: %r' % (user,))
        wantedId = user['id']
        users = self.userListPanel.users
        # Linear search, FTW!
        for index in self.orders[1]:
            if users[index]['id'] == wantedId:
                # Linear search again!
                self.orders[1].remove(index)
                self.orders[2].append(index)
                self.nFriends -= 1
                if self.currentOrder != 0:
                    # Only redisplay if we're not looking at the full list.
                    self.userListPanel.showUsers()
                self._updateFilterButtonText()
                break


class IconSizeChanger(object):
    def __init__(self, userListPanel):
        self.userListPanel = userListPanel

    def onChange(self, iconSizeBox):
        global _iconSize
        _iconSize = iconSizeBox.getValue(iconSizeBox.getSelectedIndex())
        self.userListPanel.setIconSizes()
        self.userListPanel.updateResultLink()
