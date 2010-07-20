#!/usr/bin/env python

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

from tickery.cache import TickeryCache

def printHeader(what):
    print '\n%s[ %s ]%s' %  ('-' * 5, what, '-' * (70 - len(what)))


if __name__ == '__main__':
    cache = TickeryCache('.', True, 0, None)
    cache.loadAllCaches()

    printHeader('ADDER')
    print str(cache.adderCache)

    printHeader('OID/UID/NAME')
    print str(cache.oidUidScreennameCache)

    printHeader('USERS')
    print str(cache.userCache)

    printHeader('FRIENDS')
    print str(cache.friendsIdCache)

    printHeader('QUERIES')
    print str(cache.queryCache)
