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

from twisted.internet import defer

from tickery.cacheutils import DumpingCache
from tickery import twitter

savedUserKeys = (
    u'followers_count',
    u'friends_count',
    u'id',
    u'location',
    u'name',
    u'profile_image_url',
    u'protected',
    u'screen_name',
    u'statuses_count',)


def dictSubset(d, names):
    '''Return a new dict consisting of the items in d that are in names.'''
    return dict([(key, d[key]) for key in names if key in d])


class TwitterUserCache(DumpingCache):

    def load(self, cacheFile):
        self.uidToUser = super(TwitterUserCache, self).load(cacheFile)
        if self.uidToUser is None:
            self.uidToUser = {}
            self.screennameToUser = {}
            self.setCache(self.uidToUser)
        else:
            self.screennameToUser = dict(
                (u['screen_name'].lower(), u) for u in self.uidToUser.values())

    def __str__(self):
        s = ['%d names in Twitter user cache' % len(self.screennameToUser)]
        for key in sorted(self.screennameToUser.keys()):
            item = self.screennameToUser[key]
            s.append('%s: id=%s' % (key, item['id']))
        return '\n'.join(s)

    def userByScreenname(self, screenname):
        def _add(user, expected):
            if user['screen_name'].lower() != expected:
                raise Exception(
                    'fetched screenname %r is not as expected (%r)' %
                    (user['screen_name'], expected))
            self.add(user)
            return user

        try:
            return defer.succeed(self.screennameToUser[screenname.lower()])
        except KeyError:
            d = twitter.userByScreenname(screenname)
            d.addCallback(_add, screenname.lower())
            return d

    def usersByScreennames(self, screennames):
        # Return a dict of screenname -> user or failure.
        result = {}

        def _done(what, screenname):
            result[screenname] = what

        deferreds = []
        for screenname in screennames:
            d = self.userByScreenname(screenname)
            d.addBoth(_done, screenname)
            deferreds.append(d)
        d = defer.DeferredList(deferreds)
        d.addCallback(lambda _: result)
        return d

    def userByUid(self, uid):
        def _add(user, expected):
            if user['id'] != expected:
                raise Exception(
                    'fetched id %r is not as expected (%r)' %
                    (user['id'], expected))
            self.add(user)
            return user

        try:
            return defer.succeed(self.uidToUser[uid])
        except KeyError:
            d = twitter.userById(uid)
            d.addCallback(_add, uid)
            return d

    def add(self, user):
        # import pprint; pprint.pprint(user)
        save = dictSubset(user, savedUserKeys)
        self.uidToUser[user['id']] = save
        self.screennameToUser[user['screen_name'].lower()] = save
        self.clean = False

    def removeUid(self, uid):
        if uid in self.uidToUser:
            del self.screennameToUser[
                self.uidToUser[uid]['screen_name'].lower()]
            del self.uidToUser[uid]
            self.clean = False

    def privateScreenname(self, screenname):
        d = self.userByScreenname(screenname)
        d.addCallback(lambda user: user['protected'])
        return d

    def uidByScreenname(self, screenname):
        d = self.userByScreenname(screenname)
        d.addCallback(lambda user: user['id'])
        return d

    def screennameByUid(self, uid):
        d = self.userByUid(uid)
        d.addCallback(lambda user: user['screen_name'])
        return d
