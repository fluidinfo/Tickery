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

import os, cPickle as pickle

from twisted.python import log
# xxx: from twisted.internet import task


class DumpingCache(object):
    
    def load(self, cacheFile):
        if os.path.exists(cacheFile):
            f = open(cacheFile, 'rb')
            self._cache = pickle.load(f)
            f.close()
        else:
            self._cache = None
        self._cacheFile = cacheFile
        self.clean = True
        # xxx: self._dumpLoop = task.LoopingCall(self._dump)
        # xxx: self._dumpLoopDeferred = d = self._dumpLoop.start(60, now=False)
        # Do a final dump when the dump loop is stopped. That's because the
        # cache may change between our last dump and when we're closed.
        # xxx: d.addCallback(lambda _: self._dump())
        log.msg('Dumping cache initialized. Persisting to %r.' % cacheFile)
        return self._cache
    
    def _dump(self):
        if not self.clean:
            log.msg('Dumping cache to file %r.' % self._cacheFile)
            try:
                f = open(self._cacheFile, 'wb')
            except IOError, e:
                log.err('Could not open cache file %r for saving: %s' %
                        (self._cacheFile, e))
            else:
                data = pickle.dumps(self._cache,
                                    protocol=pickle.HIGHEST_PROTOCOL)
                log.msg('Pickle string built for %r.' % self._cacheFile)
                f.write(data)
                f.close()
                log.msg('Pickle string written to %r.' % self._cacheFile)
                self.clean = True
                log.msg('Dumped cache to %r.' % self._cacheFile)

    def close(self):
        log.msg('Closing cache file %r.' % self._cacheFile)
        # xxx: self._dumpLoop.stop()
        # xxx: return self._dumpLoopDeferred
        self._dump()

    def setCache(self, thing):
        self._cache = thing


class TwoWayDictCache(DumpingCache):

    def load(self, cacheFile):
        forward = super(TwoWayDictCache, self).load(cacheFile)
        if forward is None:
            forward, backward = {}, {}
            self.setCache(forward)
        else:
            backward = dict((v.lower(), k) for k, v in forward.items())
        return forward, backward
