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

from txfluiddb.client import Endpoint, BasicCreds

from tickery.www.defaults import TWITTER_USERNAME, TWITTER_PASSWORD_VAR

def twitterPassword():
    try:
        return os.environ[TWITTER_PASSWORD_VAR]
    except KeyError:
        raise Exception('Please set %r in your environment.' %
                        TWITTER_PASSWORD_VAR)

def twitterEndpoint(URL):
    return Endpoint(baseURL=URL,
                    creds=BasicCreds(TWITTER_USERNAME, twitterPassword()))
