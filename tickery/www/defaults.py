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

TICKERY_DOMAIN = 'tickery.net'
TICKERY_URL = 'http://%s' % TICKERY_DOMAIN
TICKERY_SERVICE_PORT = 6969

# The name of the OAuth callback resource must match the callback URL
# that the Tickery app has registered at Twitter. Click on Edit
# Applications Settings (on the Twitter app site) to see the callback
# URL.
TICKERY_CALLBACK_CHILD = 'oauth-callback'
TICKERY_CALLBACK_URL = TICKERY_URL + '/' + TICKERY_CALLBACK_CHILD

OAUTH_COOKIE = 'tickery-oauth'

TWITTER_PASSWORD_VAR = 'FLUIDDB_TWITTER_PASSWORD'
TWITTER_USERNAME = u'twitter.com'
TWITTER_NAME = u'Twitter Inc.'
TWITTER_EMAIL = u'info@fluidinfo.com'
TWITTER_FRIENDS_NAMESPACE_NAME = u'friends'
TWITTER_FOLLOWERS_NAMESPACE_NAME = u'followers'
TWITTER_USERS_NAMESPACE_NAME = u'users'
# In these tag names, we match the names that Twitter uses in the JSON
# they send back when you fetch a Twitter user. These tag names are used
# (in ftwitter.py) to pull things out of Twitter responses, so you must
# use the Twitter names. That's a good thing - we want to be familiar to
# Twitter devs.
TWITTER_ID_TAG_NAME = u'id'
TWITTER_SCREENNAME_TAG_NAME = u'screen_name'
TWITTER_UPDATED_AT_TAG_NAME = u'fluiddb_updated_at'
TWITTER_N_FRIENDS_TAG_NAME = u'friends_count'
TWITTER_N_FOLLOWERS_TAG_NAME = u'followers_count'
TWITTER_N_STATUSES_TAG_NAME = u'statuses_count'
# TWITTER_LOCATION_TAG_NAME = u'location'

FLUIDDB_ENDPOINT = 'http://fluiddb.fluidinfo.com/'
SANDBOX_ENDPOINT = 'http://sandbox.fluidinfo.com/'
LOCAL_ENDPOINT   = 'http://localhost:8080/'

FRIENDS_LIMIT = 1000
RESULTS_LIMIT = 1000
