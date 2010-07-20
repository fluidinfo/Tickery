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

from twisted.python import usage

from txfluiddb.client import _HasPath


def fluidDBRootPassword():
    VAR = 'FLUIDDB_ROOT_PASSWORD'
    try:
        return os.environ[VAR]
    except KeyError:
        raise usage.UsageError('You must set a %s environment variable.' % VAR)

    
class FluidDBOptions(usage.Options):
    optParameters = [
        ['fluiddb-user', None, 'fluiddb', "The system user's name."],
        ['fluiddb-password', None, None, "The system user's password."],
        ]


class User(_HasPath):
    def __init__(self, uid, username):
        super(User, self).__init__(username)
        self.uid = uid
        
    @classmethod
    def create(cls, endpoint, username, name, password, email):
        def _parseResponse(response):
            return cls(username, response[u'id'])
        data = { 'userName' : username, 'name' : name, 
                 'password' : password, 'email' : email }
        d = endpoint.submit(endpoint.getRootURL() + 'users',
                            method='POST', data=data)
        return d.addCallback(_parseResponse)

    def getEmail(self, endpoint):
        url = self.getURL(endpoint)
        d = endpoint.submit(url=url, method='GET')
        return d.addCallback(lambda res: res[u'email'])
