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

import unknown

from pyjamas.ui.Label import Label
from pyjamas.ui.HTML import HTML


class ResultHandler(object):
    def __init__(self, query, sender, tabName, titleMaker, callback=None):
        self.query = query
        self.sender = sender
        self.tabName = tabName
        self.titleMaker = titleMaker
        self.callback = callback

    def onRemoteResponse(self, result, request_info):
        self.sender.goButton.setEnabled(True)
        if result['result']:
            self.sender.clearResults()
            if self.callback is not None:
                self.callback()
            users = result['users']
            title = self.titleMaker(users)
            if users:
                kw = {'query': self.query}
                if self.tabName == 'simple':
                    kw['screennames'] = self.sender.getNames()
                self.sender.results.setUsers(title, users, kw)
            else:
                l = HTML(title, StyleName='result-title')
                self.sender.results.add(l)
                self.sender.results.add(HTML('<a href="%s">Link</a>' %
                                             self.sender.resultsLink()))
        else:
            if 'unadded' in result:
                # Clear the former results, if any.
                self.sender.clearResults()
                self.sender.checkResult.add(
                    unknown.UnaddedUsers(result['unadded'], self.sender))
            elif 'nonexistent' in result:
                self.sender.checkResult.add(
                    unknown.NonexistentUsers(result['nonexistent']))
            elif 'protected' in result:
                self.sender.checkResult.add(
                    unknown.ProtectedUsers(result['protected']))
            elif 'othererror' in result:
                self.sender.checkResult.add(
                    unknown.OtherErrorUsers(result['othererror']))
            elif 'toomany' in result:
                self.sender.checkResult.add(
                    unknown.TooManyFriends(result['toomany'], result['limit']))
            elif 'toomanyresults' in result:
                self.sender.checkResult.add(
                    unknown.TooManyResults(result['toomanyresults'][0],
                                           result['limit']))
            elif 'offset' in result:
                self.sender.checkResult.add(
                    Label('Parse error in query, at %r, offset %d.' %
                          (result['value'], result['offset']),
                          StyleName='userlist-error-title'))
            else:
                self.sender.checkResult.add(Label(
                    'Your query could not be parsed! %r' % (result,),
                    StyleName='userlist-error-title'))

    def onRemoteError(self, code, message, request_info):
        self.sender.checkResult.add(Label(
            'Status: Server Err or Invalid Response: %s (code %d)' %
            (message, code), StyleName='userlist-error-title'))
        self.sender.goButton.setEnabled(True)
