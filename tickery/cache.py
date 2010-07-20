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

import os, functools

from twisted.internet import defer
from twisted.application import service

from txrdq.rdq import DeferredPool

from tickery.usercache import TwitterUserCache
from tickery.querycache import QueryCache
from tickery.cookiecache import CookieCache
from tickery.oidcache import OidUidScreennameCache
from tickery.adder import AdderCache
from tickery.friendscache import FriendsCache


class TickeryCache(service.Service):
    def __init__(self, cacheDir, restoreAddQueue, queueWidth, endpoint):
        self.cacheDir = cacheDir
        self.restoreAddQueue = restoreAddQueue
        self.queueWidth = queueWidth
        self.endpoint = endpoint
        # oauthTokenDict is a volatile cache.
        self.oauthTokenDict = {}
        self.extraTwitterTagsPool = DeferredPool()
        
    def startService(self):
        self.loadAllCaches()

    def loadAllCaches(self):
        service.Service.startService(self)

        cacheFile = functools.partial(os.path.join, self.cacheDir)
        
        self.userCache = TwitterUserCache()
        self.userCache.load(cacheFile('users'))
        
        self.oidUidScreennameCache = OidUidScreennameCache(self.endpoint)
        self.oidUidScreennameCache.load(cacheFile('oidUidScreenname'))
        
        self.queryCache = QueryCache()
        self.queryCache.load(cacheFile('queries'))
        
        self.cookieCache = CookieCache()
        self.cookieCache.load(cacheFile('cookies'))
        
        self.adderCache = AdderCache(self, self.queueWidth, self.endpoint)
        self.adderCache.load(cacheFile('adder'))
        
        self.friendsIdCache = FriendsCache()
        self.friendsIdCache.load(cacheFile('friends'))

    @defer.inlineCallbacks
    def stopService(self):
        yield self.adderCache.close()
        yield self.extraTwitterTagsPool.deferUntilEmpty()
        self.userCache.close()
        self.oidUidScreennameCache.close()
        self.queryCache.close()
        self.cookieCache.close()
        self.friendsIdCache.close()
        service.Service.stopService(self)
