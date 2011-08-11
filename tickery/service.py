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

import time

from txjsonrpc.web import jsonrpc

from twisted.python import log

from tickery import twitter, ftwitter
from tickery.query import ASTBuilder, TokenError, UnparseableError
from tickery.login import getTwitterOAuthURL
from tickery.www import defaults


class TooManyResults(Exception):
    pass


screennameListErrors = {
    ftwitter.NonExistentScreennames: 'nonexistent',
    ftwitter.ScreennameErrors: 'othererror',
    ftwitter.ProtectedScreennames: 'protected',
    ftwitter.TooManyFriends: 'toomany',
    TooManyResults: 'toomanyresults',
    }

_noScreenname = '<None>'


class RegularService(jsonrpc.JSONRPC):

    def __init__(self, cache, endpoint):
        jsonrpc.JSONRPC.__init__(self)
        self.cache = cache
        self.endpoint = endpoint
        self.ASTBuilder = ASTBuilder()

    def jsonrpc_nUsers(self):
        return {'result': self.cache.oidUidScreennameCache.nUsers()}

    def jsonrpc_spideredScreennames(self, *screennames):
        log.msg('spideredScreenname called with %r.' % (screennames,))
        return {'result':
                [self.cache.adderCache.added(s) for s in screennames]}

    def _objectIdsToUsers(self, (users, ids)):
        '''Convert a list of Fluidinfo object ids to a JSON RPC result dict
        containing a list of Twitter screennames.'''
        if ids:
            log.err('Unexpected object ids matched query: %r' % (ids,))
        return {
            'result': {
                'result': True,
                'users': users}}

    def jsonrpc_friendOf(self, screenname1, screenname2):
        """
        Does screenname1 follow screenname2?

        @param screenname1: A C{str} Twitter screen name.

        @param screenname2: A C{str} Twitter screen name.

        @return: a C{Deferred} that fires with C{True} if screenname1 follows
        screenname2 (i.e., screenname2 is a friend of screenname1) and with
        C{False} otherwise.
        """
        log.msg('FriendOf %r and %r.' % (screenname1, screenname2))
        d = ftwitter.friendOf(self.cache, self.endpoint,
                              unicode(screenname1), unicode(screenname2))
        d.addCallback(lambda result: {'result': result})
        d.addErrback(log.err)
        return d

    def _checkTooManyResults(self, results):
        n = len(results)
        if n > defaults.RESULTS_LIMIT:
            # We need to raise with a list arg, because we're going to fail
            # here and be caught by _screennameListError, which wants a
            # list of user names for its error return value.
            raise TooManyResults([n])
        else:
            return results

    def _screennameListError(self, fail):
        listErr = fail.trap(*screennameListErrors.keys())
        result = {
            'result': {
                'result': False,
                screennameListErrors[listErr]: list(fail.value.args[0]),
                }
            }
        # Add the current friends limit if we have that kind of error.
        if listErr is ftwitter.TooManyFriends:
            result['result']['limit'] = defaults.FRIENDS_LIMIT
        elif listErr is TooManyResults:
            result['result']['limit'] = defaults.RESULTS_LIMIT
        return result

    def _unaddedError(self, fail):
        fail.trap(ftwitter.UnaddedScreennames)
        return {
            'result': {
                'result': False,
                'unadded': fail.value.args[0],
                }
            }

    def jsonrpc_intermediateQuery(self, cookie, tabName, query):
        try:
            data = self.cache.cookieCache[cookie]
        except KeyError:
            screenname = _noScreenname
        else:
            screenname = data[0]['screen_name']

        log.msg('QUERY: tab=%s user=%r query=%r' % (
            tabName, screenname, query))

        try:
            parseTree = self.ASTBuilder.build(query)
        except TokenError, p:
            log.msg('User %r sent malformed query %r' % (screenname, query))
            return {
                'result': {
                    'result': False,
                    'value': p.value,
                    'offset': p.offset,
                    }
                }
        except UnparseableError:
            log.msg('User %r sent unparsable query %r' % (screenname, query))
            return {
                'result': {
                    'result': False,
                    }
                }
        else:
            d = ftwitter.intermediateQuery(
                self.cache, self.endpoint, parseTree)
            d.addCallback(self._checkTooManyResults)
            d.addCallback(
                self.cache.oidUidScreennameCache.objectIdsToUsers,
                self.cache.userCache)
            d.addCallback(self._objectIdsToUsers)
            d.addErrback(self._screennameListError)
            d.addErrback(self._unaddedError)
            d.addErrback(log.err)
            return d

    def _fluidinfoError(self, fail, query):
        err = fail.check(ftwitter.FluidinfoParseError,
                         ftwitter.FluidinfoError,
                         ftwitter.FluidinfoNonexistentAttribute,
                         ftwitter.FluidinfoPermissionDenied)
        if err is None:
            log.msg('Error on Fluidinfo query %r:' % query)
            log.err(fail)
            errorClass = 'unknown'
        else:
            errorClass = err.__name__
        return {
            'result': {
                'result': False,
                'errorClass': errorClass,
                }
            }

    def jsonrpc_fluidinfoQuery(self, cookie, tabName, query):
        try:
            data = self.cache.cookieCache[cookie]
        except KeyError:
            screenname = _noScreenname
        else:
            screenname = data[0]['screen_name']
        log.msg('QUERY: tab=%s user=%r query=%r' % (
            tabName, screenname, query))
        d = ftwitter.fluidinfoQuery(self.endpoint, query)
        d.addCallback(self._checkTooManyResults)
        d.addCallback(
            self.cache.oidUidScreennameCache.objectIdsToUsers,
            self.cache.userCache)
        d.addCallback(self._objectIdsToUsers)
        d.addErrback(self._screennameListError)  # Catches TooManyResults
        d.addErrback(self._fluidinfoError, query)
        return d

    def _loginRedirectURL(self, URL):
        return {
                'result': {
                    'result': True,
                    'URL': URL,
                    }
                }

    def _loginRedirectErr(self, failure):
        return {
                'result': {
                    'result': False,
                    'error': str(failure),
                    }
                }

    def jsonrpc_login(self):
        d = getTwitterOAuthURL(self.cache.oauthTokenDict)
        d.addCallbacks(self._loginRedirectURL, self._loginRedirectErr)
        return d

    def jsonrpc_screenameFromCookie(self, cookie):
        try:
            data = self.cache.cookieCache[cookie]
        except KeyError:
            return {
                'result': {
                    'result': False,
                    }
                }
        else:
            user, _ = data
            return {
                'result': {
                    'result': True,
                    'screen_name': user['screen_name'],
                    }
                }

    def jsonrpc_logout(self, cookie):
        try:
            data = self.cache.cookieCache[cookie]
        except:
            pass
        else:
            del self.cache.cookieCache[cookie]
            user, _ = data
            log.msg('Logging out user %r.' % user['screen_name'])
        return {
                'result': True,
            }

    def _tweetURL(self, response):
        import pprint
        log.msg('Update got response %s' % pprint.pformat(response))
        return {
                'result': {
                    'result': True,
                    'URL': twitter.statusURLFromUpdateResponse(response),
                    }
                }

    def _tweetError(self, failure):
        return {
                'result': {
                    'result': False,
                    'error': str(failure),
                    }
                }

    def jsonrpc_simpleTweet(self, cookie, screennames, nUsers, sortKey,
                            useAtSigns):
        d = ftwitter.simpleUpdate(cookie, self.cache.cookieCache,
                                  screennames, nUsers, sortKey, useAtSigns)
        d.addCallbacks(self._tweetURL, self._tweetError)
        return d

    def jsonrpc_tweet(self, cookie, text, query, tabName, sortKey):
        d = ftwitter.update(cookie, self.cache.cookieCache, text, query,
                            tabName, sortKey)
        d.addCallbacks(self._tweetURL, self._tweetError)
        return d

    def jsonrpc_friendsIds(self, cookie, screenname):
        '''Get the list of ids of people who screenname is following.'''
        log.msg('Getting friend ids for %r.' % screenname)
        d = ftwitter.friendsIdFetcher(cookie, self.cache, screenname)
        d.addCallback(lambda friendsIds: {
            'result': {'friendsIds': friendsIds},
            })
        return d

    def jsonrpc_follow(self, cookie, uid):
        log.msg('Following uid %r.' % uid)
        d = twitter.follow(cookie, self.cache, uid)
        d.addCallback(lambda _: ftwitter.follow(cookie, self.cache,
                                                self.endpoint, uid))
        d.addCallback(lambda _: {'result': True})
        return d

    def jsonrpc_unfollow(self, cookie, uid):
        log.msg('Unfollowing uid %r.' % uid)
        d = twitter.unfollow(cookie, self.cache, uid)
        d.addCallback(lambda _: ftwitter.unfollow(cookie, self.cache,
                                                  self.endpoint, uid))
        d.addCallback(lambda _: {'result': True})
        return d


class AdminService(jsonrpc.JSONRPC):

    def __init__(self, cache):
        jsonrpc.JSONRPC.__init__(self)
        self.cache = cache

    def jsonrpc_getQueueWidth(self):
        return {'result': self.cache.adderCache.rdq.width}

    def jsonrpc_setQueueWidth(self, width):
        try:
            width = int(width)
        except ValueError:
            return {'result': False}
        else:
            self.cache.adderCache.rdq.width = width
            return {'result': True}

    def jsonrpc_queueSize(self):
        return {'result': self.cache.adderCache.rdq.size()}

    def jsonrpc_queuePaused(self):
        return {'result': self.cache.adderCache.rdq.paused}

    def jsonrpc_pause(self):
        d = self.cache.adderCache.rdq.pause()
        d.addCallback(lambda _: {'result': True})
        return d

    def jsonrpc_resume(self):
        self.cache.adderCache.rdq.resume()
        return {'result': True}

    def jsonrpc_getQueued(self):
        pendingJobs = self.cache.adderCache.rdq.pending()
        result = [[pj.jobarg.screenname, pj.jobarg.nFriends,
                   time.ctime(pj.queuedTime)] for pj in pendingJobs]
        return {'result': result}

    def jsonrpc_getUnderway(self):
        underwayJobs = self.cache.adderCache.rdq.underway()
        result = []
        for job in underwayJobs:
            user = job.jobarg
            pct = 100.0 * float(user.workDone) / float(user.workToDo)
            result.append([
                user.screenname,
                user.nFriends,
                pct,
                time.ctime(job.queuedTime),
                time.ctime(job.startTime)]
                )
        return {'result': result}

    def jsonrpc_getMaxRequestsLimit(self):
        return {'result': ftwitter.MAX_SIMULTANEOUS_REQUESTS}

    def jsonrpc_setMaxRequestsLimit(self, limit):
        try:
            ftwitter.MAX_SIMULTANEOUS_REQUESTS = int(limit)
        except ValueError:
            return {'result': False}
        else:
            return {'result': True}

    def jsonrpc_getFriendsLimit(self):
        return {'result': defaults.FRIENDS_LIMIT}

    def jsonrpc_setFriendsLimit(self, limit):
        try:
            defaults.FRIENDS_LIMIT = int(limit)
        except ValueError:
            return {'result': False}
        else:
            return {'result': True}

    def jsonrpc_getResultsLimit(self):
        return {'result': defaults.RESULTS_LIMIT}

    def jsonrpc_setResultsLimit(self, limit):
        try:
            defaults.RESULTS_LIMIT = int(limit)
        except ValueError:
            return {'result': False}
        else:
            return {'result': True}

    def jsonrpc_directAddUser(self, screenname):
        def _err(fail):
            return {
                'error': None,
                'message': str(fail.value),
                }

        def _ok(result):
            return {
                'result': True,
                }

        d = ftwitter.directAddUser(self.cache, unicode(screenname))
        d.addCallbacks(_ok, _err)
        return d

    def jsonrpc_bulkAddUsers(self, screennames):
        # Add a bunch of users in bulk.
        def _ret(errs):
            log.msg('Errs is %r' % (errs,))
            if errs:
                return {
                    'message': errs,
                    }
            else:
                return {
                    'result': True,
                    }

        d = ftwitter.bulkAddUsers(
            self.cache, map(unicode, screennames.split()))
        d.addCallback(_ret)
        return d

    def jsonrpc_cancel(self, screenname):
        try:
            self.cache.adderCache.cancel(screenname)
        except Exception, e:
            return {
                'message': str(e)
                }
        else:
            return {
                'result': True,
                }
