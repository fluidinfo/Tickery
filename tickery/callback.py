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

import uuid
try:
    import json
    _ = json  # Keep pyflakes quiet about redefinition of unused json.
except ImportError:
    import simplejson as json

from twisted.python import log
from twisted.web import resource, client, server

from txretry.retry import RetryingCall

from tickery import twitter, oauth, consumer, signature
from tickery.www import defaults


class Callback(resource.Resource):

    isLeaf = True

    def __init__(self, cache):
        self.cache = cache
        self.domain = defaults.TICKERY_DOMAIN
        self.redirectURL = defaults.TICKERY_URL

    def render_GET(self, request):
        # The cookie cache is actually only available once the cache
        # service has started. But that should happen before we get any
        # requests.
        log.err('Callback received: %s' % request)

        oauthToken = request.args['oauth_token']
        if oauthToken:
            oauthToken = oauthToken[0]
        else:
            log.err('Received callback with no oauth_token: %s' % request)
            raise Exception('Received callback with no oauth_token.')

        oauthVerifier = request.args['oauth_verifier']
        if oauthVerifier:
            oauthVerifier = oauthVerifier[0]
        else:
            log.err('Received callback with no oauth_verifier: %s' % request)
            raise Exception('Received callback with no oauth_verifier.')

        try:
            token = self.cache.oauthTokenDict.pop(oauthToken)
        except KeyError:
            log.err('Received callback with unknown oauth_token: %s' %
                    oauthToken)
            raise Exception('Received callback with unknown oauth_token.')

        oaRequest = oauth.OAuthRequest.from_consumer_and_token(
            consumer.consumer, token=token, verifier=oauthVerifier,
            http_url=twitter.ACCESS_TOKEN_URL)
        oaRequest.sign_request(
            signature.hmac_sha1, consumer.consumer, token)
        log.msg('Requesting access token.')
        r = RetryingCall(
            client.getPage, oaRequest.to_url(), headers=oaRequest.to_header())
        d = r.start()
        d.addCallback(self._storeAccessToken, request)
        d.addErrback(log.err)
        return server.NOT_DONE_YET

    def _storeAccessToken(self, result, request):
        accessToken = oauth.OAuthToken.from_string(result)
        log.msg('Got access token: %s' % accessToken)
        oaRequest = oauth.OAuthRequest.from_consumer_and_token(
            consumer.consumer, token=accessToken,
            http_url=twitter.VERIFY_CREDENTIALS_URL)
        oaRequest.sign_request(
            signature.hmac_sha1, consumer.consumer, accessToken)
        log.msg('Verifying credentials.')
        r = RetryingCall(client.getPage, oaRequest.to_url())
        d = r.start()
        d.addCallback(self._storeUser, accessToken, request)
        d.addErrback(log.err)
        return d

    def _storeUser(self, result, accessToken, request):
        user = json.loads(result)
        # import pprint
        # log.msg('Got user: %s' % pprint.pformat(user))
        key = str(uuid.uuid4())
        self.cache.cookieCache[key] = (user, accessToken)
        log.msg('Setting cookie %s' % key)
        request.addCookie(defaults.OAUTH_COOKIE, key, path='/',
                          domain=self.domain)
        request.redirect(self.redirectURL)
        log.msg('Redirecting to %s' % self.redirectURL)
        request.finish()
