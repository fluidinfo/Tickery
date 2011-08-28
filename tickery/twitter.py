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

import functools
try:
    import json
    _ = json  # Keep pyflakes quiet about redefinition of unused json.
except ImportError:
    import simplejson as json
import time
import urllib

from twisted.internet import defer
from twisted.internet.error import ConnectionLost
from twisted.web import client, error, http
from twisted.python import log, failure

from txretry.retry import RetryingCall

from tickery.www import defaults
from tickery import oauth, consumer, signature, version, error as terror

# OAuth URLs
TWITTER_URL = 'http://twitter.com'
REQUEST_TOKEN_URL = TWITTER_URL + '/oauth/request_token'
AUTHORIZATION_URL = TWITTER_URL + '/oauth/authorize'
ACCESS_TOKEN_URL = TWITTER_URL + '/oauth/access_token'

# API URLs
TWITTER_API_URL = 'http://api.twitter.com/1'
VERIFY_CREDENTIALS_URL = TWITTER_API_URL + '/account/verify_credentials.json'
UPDATE_STATUS_URL = TWITTER_API_URL + '/statuses/update.json'
FOLLOW_URL = TWITTER_API_URL + '/friendships/create.json'
UNFOLLOW_URL = TWITTER_API_URL + '/friendships/destroy.json'

okErrs = (http.INTERNAL_SERVER_ERROR, http.BAD_GATEWAY,
          http.SERVICE_UNAVAILABLE, http.GATEWAY_TIMEOUT)

POSTHeaders = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    'X-Twitter-Client': 'Tickery',
    'X-Twitter-Client-Version': version.version,
    'X-Twitter-Client-URL': defaults.TICKERY_URL,
    }


class _Fetcher(object):
    baseURL = TWITTER_API_URL + '/'
    URITemplate = None  # Override in subclass.
    dataKey = None  # Override in subclass.
    headers = {}
    maxErrs = 10

    def __init__(self, name, token=None):
        assert self.baseURL.endswith('/')
        self.start = time.time()
        self.results = []
        self.errCount = 0
        self.nextCursor = -1
        self.deferred = defer.Deferred()
        self.URL = self.baseURL + (
            self.URITemplate % {'name': urllib.quote(name.encode('utf-8'))})
        self.token = token

    def _reportElapsed(self, result):
        log.msg('Twitter API: status=%s elapsed=%.03f URL=%s' %
                ('FAIL' if isinstance(result, failure.Failure) else 'OK',
                 time.time() - self.start, self.URL))
        return result

    def _fail(self, fail):
        err = fail.trap(error.Error, ConnectionLost)
        self.errCount += 1
        if (self.errCount < self.maxErrs and
            (err is ConnectionLost or int(fail.value.status) in okErrs)):
            self.fetch()
        else:
            self.deferred.errback(fail)

    def _parse(self, result):
        try:
            data = json.loads(result)
            self.nextCursor = data.get('next_cursor')
            self.results.extend(data[self.dataKey])
        except Exception:
            self.deferred.errback()
        else:
            self.fetch()

    def _deDup(self):
        raise NotImplementedError('Override _deDup in subclasses.')

    def fetch(self):
        if self.nextCursor:
            url = self.URL + '?cursor=%s' % self.nextCursor
            headers = {}
            if self.token:
                oaRequest = oauth.OAuthRequest.from_consumer_and_token(
                    consumer.consumer, token=self.token,
                    http_url=url, http_method='GET')
                oaRequest.sign_request(
                    signature.hmac_sha1, consumer.consumer, self.token)
                headers.update(oaRequest.to_header())

            d = client.getPage(url, headers=headers)
            d.addBoth(self._reportElapsed)
            d.addCallback(self._parse)
            d.addErrback(self._fail)
        else:
            self.deferred.callback(self._deDup())
        return self.deferred


class _FriendsOrFollowersFetcher(_Fetcher):
    dataKey = u'users'

    def _deDup(self):
        #  The 'seen' set is to avoid duplicates.
        seen = set()
        result = []
        for userdict in self.results:
            uid = userdict['id']
            if uid not in seen:
                result.append(userdict)
                seen.add(uid)
        return result


class _IdFetcher(_Fetcher):
    dataKey = u'ids'

    def _deDup(self):
        # Keep the ids in the order we received them. The 'seen' set is to
        # avoid duplicates.
        seen = set()
        result = []
        for uid in self.results:
            if uid not in seen:
                result.append(uid)
                seen.add(uid)
        return result


class FriendsFetcher(_FriendsOrFollowersFetcher):
    URITemplate = 'statuses/friends/%(name)s.json'


class FollowersFetcher(_FriendsOrFollowersFetcher):
    URITemplate = 'statuses/followers/%(name)s.json'


class FriendsIdFetcher(_IdFetcher):
    URITemplate = 'friends/ids/%(name)s.json'


class FollowersIdFetcher(_IdFetcher):
    URITemplate = 'followers/ids/%(name)s.json'


class AllowOne404Tester(object):
    def __init__(self):
        self.seen404 = False

    def test(self, fail):
        # Don't return a result in order to ignore a fail that should
        # be retried.
        err = fail.trap(error.Error, ConnectionLost)
        if err is not ConnectionLost:
            status = int(fail.value.status)
            if status == http.NOT_FOUND:
                if self.seen404:
                    return fail
                else:
                    self.seen404 = True
            elif status not in okErrs:
                return fail


def userByScreenname(screenname):
    r = RetryingCall(
        client.getPage,
        '%s/users/show.json?screen_name=%s' %
        (TWITTER_API_URL, urllib.quote(screenname.encode('utf-8'))))
    tester = AllowOne404Tester()
    d = r.start(failureTester=tester.test)
    d.addCallback(lambda j: json.loads(j))
    return d


def userById(uid):
    r = RetryingCall(
        client.getPage,
        '%s/users/show.json?user_id=%s' % (TWITTER_API_URL, uid))
    tester = AllowOne404Tester()
    d = r.start(failureTester=tester.test)
    d.addCallback(lambda j: json.loads(j))
    return d


def _urlencodeDict(d):
    result = []
    for k, v in d.iteritems():
        result.append('%s=%s' % (urllib.quote(k.encode("utf-8")),
                                 urllib.quote(v.encode("utf-8"))))
    return '&'.join(result)


def updateStatus(status, cookie, cookieDict):
    log.msg('Sending tweet %r' % status)
    try:
        _, accessToken = cookieDict[cookie]
    except KeyError:
        log.err('updateStatus: Could not find cookie' % cookie)
        return defer.fail(terror.NoSuchCookie())

    parameters = {'status': status}
    oaRequest = oauth.OAuthRequest.from_consumer_and_token(
        consumer.consumer, token=accessToken, parameters=parameters,
        http_url=UPDATE_STATUS_URL, http_method='POST')
    oaRequest.sign_request(
        signature.hmac_sha1, consumer.consumer, accessToken)
    headers = POSTHeaders.copy()
    headers.update(oaRequest.to_header())

    # r = RetryingCall(client.getPage, UPDATE_STATUS_URL, method='POST',
    # headers=headers, postdata=_urlencodeDict(parameters))
    # d = r.start()
    d = client.getPage(UPDATE_STATUS_URL, method='POST', headers=headers,
                       postdata=_urlencodeDict(parameters))
    d.addCallback(lambda j: json.loads(j))
    return d


def statusURLFromUpdateResponse(response):
    'Response is the JSON returned by a statuses/update.json API call.'
    return '%s/%s/status/%s' % (
        TWITTER_API_URL,
        urllib.quote(response[u'user'][u'screen_name'].encode('utf-8')),
        response[u'id'])


def _updateUserCache_cb(user, cache):
    cache.userCache.add(user)
    return user


def _invalidateResultCache_cb(result, cache, screenname):
    cache.queryCache.invalidateQueriesForScreenname(screenname)
    return result


def _followOrUnfollow(follow, cookie, cache, uid):
    try:
        user, accessToken = cache.cookieCache[cookie]
    except KeyError:
        log.err('followOrUnfollow: Could not find cookie' % cookie)
        return defer.fail(terror.NoSuchCookie())

    if follow:
        url = FOLLOW_URL
    else:
        url = UNFOLLOW_URL

    parameters = {'user_id': str(uid)}
    oaRequest = oauth.OAuthRequest.from_consumer_and_token(
        consumer.consumer, token=accessToken, parameters=parameters,
        http_url=url, http_method='POST')
    oaRequest.sign_request(
        signature.hmac_sha1, consumer.consumer, accessToken)
    headers = POSTHeaders.copy()
    headers.update(oaRequest.to_header())

    # r = RetryingCall(client.getPage, UPDATE_STATUS_URL, method='POST',
    # headers=headers, postdata=_urlencodeDict(parameters))
    # d = r.start()
    d = client.getPage(url, method='POST', headers=headers,
                       postdata=_urlencodeDict(parameters))
    d.addCallback(lambda j: json.loads(j))
    d.addCallback(_updateUserCache_cb, cache)
    d.addCallback(_invalidateResultCache_cb, cache, user['screen_name'])
    return d

follow = functools.partial(_followOrUnfollow, True)
unfollow = functools.partial(_followOrUnfollow, False)
