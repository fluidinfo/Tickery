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

from tickery import twitter
from tickery.cacheutils import DumpingCache


class FriendsCache(DumpingCache):
    
    def load(self, cacheFile):
        self._friends = super(FriendsCache, self).load(cacheFile)
        if self._friends is None:
            self._friends = {}
            self.setCache(self._friends)

    def __getitem__(self, screenname):
        try:
            return defer.succeed(self._friends[screenname.lower()])
        except KeyError:
            def _add(result):
                self._friends[screenname.lower()] = result
                self.clean = False
                return result
            # Note that we only do unauthenticated requests, so we can
            # safely cache results.
            fetcher = twitter.FriendsIdFetcher(screenname)
            d = fetcher.fetch()
            d.addCallback(_add)
            return d

    def __str__(self):
        s = [ '%d names in friends cache' % len(self._friends) ]
        for key in sorted(self._friends.keys()):
            s.append('%s: nFriends=%s' % (key, len(self._friends[key])))
        return '\n'.join(s)
