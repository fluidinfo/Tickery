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


from tickery.options import EndpointOptions

from twisted.internet import reactor, defer
from twisted.web import http, error

from txfluiddb.client import Endpoint, BasicCreds, Namespace

from tickery.endpoint import twitterPassword
from tickery.www.defaults import (TWITTER_FRIENDS_NAMESPACE_NAME,
    TWITTER_FOLLOWERS_NAMESPACE_NAME, TWITTER_USERS_NAMESPACE_NAME,
    TWITTER_SCREENNAME_TAG_NAME, TWITTER_ID_TAG_NAME,
    TWITTER_UPDATED_AT_TAG_NAME, TWITTER_USERNAME, TWITTER_N_FRIENDS_TAG_NAME,
    TWITTER_N_FOLLOWERS_TAG_NAME, TWITTER_N_STATUSES_TAG_NAME)


class Options(EndpointOptions):
    pass


def report(result, msg):
    print msg
    return result

def ignorePreexistingErrror(failure, msg):
    failure.trap(error.Error)
    if int(failure.value.status) == http.PRECONDITION_FAILED:
        print 'Ignoring precondition error (encountered in %r)' % (msg,)
    else:
        return failure

def addCallbacks(d, msg):
    d.addCallbacks(report, ignorePreexistingErrror,
                   callbackArgs=(msg,), errbackArgs=(msg,))

@defer.inlineCallbacks
def create(endpoint):
    ns = Namespace(TWITTER_USERNAME)
    d = ns.createChild(endpoint, TWITTER_FRIENDS_NAMESPACE_NAME,
                       'Holds tags for users to indicate friends.')
    addCallbacks(d, 'Created friends namespace %r.' %
                 TWITTER_FRIENDS_NAMESPACE_NAME)
    yield d
    
    d = ns.createChild(endpoint, TWITTER_FOLLOWERS_NAMESPACE_NAME,
                       'Holds tags for users to indicate followers.')
    addCallbacks(d, 'Created followers namespace %r.' %
                 TWITTER_FOLLOWERS_NAMESPACE_NAME)
    yield d

    d = ns.createChild(endpoint, TWITTER_USERS_NAMESPACE_NAME,
                       'Holds tags for info about Twitter users.')
    addCallbacks(d, 'Created users namespace %r.' %
                 TWITTER_USERS_NAMESPACE_NAME)
    yield d

    # createChild (above) will return a Namespace when txFluidDB gets fixed.
    userNs = ns.child(TWITTER_USERS_NAMESPACE_NAME)

    for name, desc in (
        (TWITTER_ID_TAG_NAME, 'Twitter user id.'),
        (TWITTER_SCREENNAME_TAG_NAME, 'Twitter screen name.'),
        (TWITTER_UPDATED_AT_TAG_NAME,
         'Time (in seconds) of last update of this user in FluidDB.'),
        (TWITTER_N_FRIENDS_TAG_NAME, 'Number of friends of a Twitter user.'),
        (TWITTER_N_FOLLOWERS_TAG_NAME,
         'Number of followers of a Twitter user.'),
        (TWITTER_N_STATUSES_TAG_NAME,
         'Number of status updates of a Twitter user.')):
        
        d = userNs.createTag(endpoint, name, desc, False)
        addCallbacks(d, 'Created tag %r.' % name)
        yield d
    

if __name__ == '__main__':

    def nok(failure):
        print 'Failed:', failure
        if hasattr(failure.value, 'response_headers'):
            foundFluidDBHeader = False
            for header in failure.value.response_headers:
                if header.startswith('x-fluiddb-'):
                    foundFluidDBHeader = True
                    print '\t%s: %s' % (
                        header, failure.value.response_headers[header][0])
            if not foundFluidDBHeader:
                print 'Headers: %r' % (failure.value.response_headers)
        else:
            return failure

    def stop(_):
        reactor.stop()

    options = Options()
    options.parseOptions()
    creds = BasicCreds(TWITTER_USERNAME, twitterPassword())
    endpoint = Endpoint(baseURL=options['endpoint'], creds=creds)
    d = create(endpoint)
    d.addCallback(report, 'Done.')
    d.addErrback(nok)    
    d.addBoth(stop)
    reactor.run()
