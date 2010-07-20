#!/usr/bin/python

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

import pprint

if __name__ == '__main__':
    import sys
    from twisted.internet import reactor
    from tickery.twitter import FriendsFetcher, FollowersFetcher

    def ok(names):
        pprint.pprint(names)

    def nok(failure):
        print 'Failed:', failure

    def stop(_):
        reactor.stop()

    if len(sys.argv) != 2:
        raise Exception('I need a single username argument.')

    if sys.argv[0].find('friends') == -1:
        fetchClass = FollowersFetcher
    else:
        fetchClass = FriendsFetcher
    ff = fetchClass(sys.argv[1])
    d = ff.fetch()
    d.addCallback(ok)
    d.addErrback(nok)
    d.addBoth(stop)
    reactor.run()
