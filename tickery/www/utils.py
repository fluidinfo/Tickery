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

import urllib

def screennameToTwitterURL(s):
    return 'http://twitter.com/%s' % urllib.quote(s)

def screennameToTwitterLink(s, text=None):
    text = text or s
    return '<a href="%s">%s</a>' % (screennameToTwitterURL(s), text)

def screennameToTwitterFriendsLink(s, text):
    return '<a href="%s/following">%s</a>' % (screennameToTwitterURL(s), text)

def screennameToTwitterFollowersLink(s, text):
    return '<a href="%s/followers">%s</a>' % (screennameToTwitterURL(s), text)

def splitthousands(n, sep=','):
    # From http://code.activestate.com/recipes/498181/
    s = '%s' % n  # This to keep MSIE quiet?
    if len(s) <= 3:
        return s
    else:
        return splitthousands(s[:-3], sep) + sep + s[-3:]
