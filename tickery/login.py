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

from twisted.python import log
from twisted.web import client

from txretry.retry import RetryingCall

from tickery import twitter, oauth, consumer, signature
from tickery.www import defaults


def getTwitterOAuthURL(oauthTokenDict):
    log.msg('Got login URL request.')

    def _cb(result):
        token = oauth.OAuthToken.from_string(result)
        # Store the token so we have the oauth_secret when the callback comes.
        oauthTokenDict[token.key] = token
        request = oauth.OAuthRequest.from_token_and_callback(
            token=token, http_url=twitter.AUTHORIZATION_URL)
        url = request.to_url()
        log.msg('Browser Twitter auth redirect URL = %r' % url)
        return url

    request = oauth.OAuthRequest.from_consumer_and_token(
        consumer.consumer, callback=defaults.TICKERY_CALLBACK_URL,
        http_url=twitter.REQUEST_TOKEN_URL)
    request.sign_request(signature.hmac_sha1, consumer.consumer, None)

    r = RetryingCall(
        client.getPage, twitter.REQUEST_TOKEN_URL, headers=request.to_header())
    d = r.start()
    d.addCallback(_cb)
    return d
