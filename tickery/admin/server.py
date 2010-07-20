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

from pyjamas.JSONService import JSONProxy

        
class AdminService(JSONProxy):
    def __init__(self):
        JSONProxy.__init__(self, '/admin/tickery',
            ['getQueueWidth', 'setQueueWidth', 'queueSize', 'queuePaused',
             'pause', 'resume', 'getQueued', 'getUnderway',
             'setMaxRequestsLimit', 'getMaxRequestsLimit',
             'setFriendsLimit', 'getFriendsLimit',
             'setResultsLimit', 'getResultsLimit', 'directAddUser',
             'bulkAddUsers', 'cancel'])
