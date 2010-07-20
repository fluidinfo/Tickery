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

from tickery.cacheutils import DumpingCache


class QueryCache(DumpingCache):
    
    def load(self, cacheFile):
        data = super(QueryCache, self).load(cacheFile)
        if data is None:
            self._queries = {}
            self._screennameIndex = {}
            self.setCache([self._queries, self._screennameIndex])
        else:
            self._queries, self._screennameIndex = data

    def __str__(self):
        s = [ '%d queries in cache' % len(self._queries) ]
        for key in sorted(self._queries.keys()):
            s.append('size %4d: %s' % (len(self._queries[key]), key))
        return '\n'.join(s)

    def __getitem__(self, query):
        return self._queries[query]

    def store(self, query, result, screennames):
        self._queries[query] = result
        for screenname in screennames:
            try:
                self._screennameIndex[screenname].append(query)
            except KeyError:
                self._screennameIndex[screenname] = [ query ]
        self.clean = False

    def invalidate(self, screenname):
        log.msg('Invalidating stored results involving %r.' % screenname)
        if screenname in self._screennameIndex:
            queries = self._queries
            for query in self._screennameIndex[screenname]:
                log.msg('Invalidating query %r.' % query)
                del queries[query]
            del self._screennameIndex[screenname]
            self.clean = False
        else:
            log.msg('There were no stored results involving %r.' % screenname)
    
    def lookupQueryResult(self, query):
        return self._queries[query]

    def storeQueryResult(self, query, result, screennames):
        self.store(query, result, screennames)

    def invalidateQueriesForScreenname(self, screenname):
        return self.invalidate(screenname)
