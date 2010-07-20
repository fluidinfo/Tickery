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

import os

from tickery import oauth

TICKERY_CONSUMER_KEY_ENV_VAR = 'TICKERY_CONSUMER_KEY'
TICKERY_CONSUMER_SECRET_ENV_VAR = 'TICKERY_CONSUMER_SECRET'


class TickeryConsumer(object):
    def __init__(self):
        key = os.environ.get(TICKERY_CONSUMER_KEY_ENV_VAR)
        if key is None:
            raise Exception('Please set %r in your environment.' %
                            TICKERY_CONSUMER_KEY_ENV_VAR)
        secret = os.environ.get(TICKERY_CONSUMER_SECRET_ENV_VAR)
        if secret is None:
            raise Exception('Please set %r in your environment.' %
                            TICKERY_CONSUMER_SECRET_ENV_VAR)
        
        self.consumer = oauth.OAuthConsumer(key, secret)    

consumer = TickeryConsumer().consumer
