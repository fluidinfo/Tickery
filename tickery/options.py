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

from twisted.python import usage

from tickery.www import defaults


class EndpointOptions(usage.Options):
    optParameters = [
        ['endpoint', None, None, 'The FluidDB endpoint URL.'],
        ]
    optFlags = [
        ['local', 'L', 'If True use the a local FluidDB'],
        ['sandbox', 'S', 'If True use the sandbox FluidDB'],
        ]

    def postOptions(self):
        endpointURL = self['endpoint']
        local = self['local']
        sandbox = self['sandbox']
        
        if endpointURL:
            assert not (local or sandbox)
        else:
            if local or sandbox:
                assert not (local and sandbox)
                if local:
                    endpointURL = defaults.LOCAL_ENDPOINT
                else:
                    endpointURL = defaults.SANDBOX_ENDPOINT
            else:
                endpointURL = defaults.FLUIDDB_ENDPOINT            
        if not endpointURL.endswith('/'):
            endpointURL += '/'
        self['endpoint'] = endpointURL
