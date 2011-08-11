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

from tickery.cacheutils import DumpingCache


class CookieCache(DumpingCache):

    def load(self, cacheFile):
        self._cookies = super(CookieCache, self).load(cacheFile)
        if self._cookies is None:
            self._cookies = {}
            self.setCache(self._cookies)

    def __getitem__(self, cookie):
        return self._cookies[cookie]

    def __delitem__(self, cookie):
        del self._cookies[cookie]
        self.clean = False

    def __setitem__(self, cookie, result):
        self._cookies[cookie] = result
        self.clean = False
