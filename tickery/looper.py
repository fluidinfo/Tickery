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

from operator import mul
from functools import partial
import time

from twisted.internet import reactor, defer, task
from twisted.python import log, failure

def simpleBackoffIterator(maxResults=10, maxDelay=120.0, now=True,
                          initDelay=0.01, incFunc=None):
    assert maxResults > 0
    remaining = maxResults
    delay = initDelay
    incFunc = incFunc or partial(mul, 2.0)
    
    if now:
        yield 0.0
        remaining -= 1
        
    while remaining > 0:
        if delay < maxDelay:
            value = delay
        else:
            value = maxDelay
        yield value
        delay = incFunc(delay)
        remaining -= 1
        

class RetryingCall(object):
    """Calls a function repeatedly, passing it args and kw args. Failures
    are passed to a user-supplied failure testing function. If the failure
    is ignored, the function is called again after a delay whose duration
    is obtained from a user-supplied iterator. The start method (below)
    returns a deferred that fires with the eventual non-error result of
    calling the supplied function, or fires its errback if no successful
    result can be obtained before the delay backoff iterator raises
    StopIteration.
    """
    def __init__(self, f, *args, **kw):
        self._f = f
        self._args = args
        self._kw = kw
        self._start = time.time()

    def _reportElapsed(self, result):
        try:
            name = self._f.__name__
        except AttributeError:
            # Maybe we were passed an instance of a callable class.
            try:
                name = self._f.__class__.__name__
            except AttributeError:
                name = 'unknown-function-name'
            
        log.msg('Retrying call %s(%r %r): status=%s elapsed=%.03f' %
                (name, self._args, self._kw,
                 'FAIL' if isinstance(result, failure.Failure) else 'OK',
                 time.time() - self._start))
        return result
        
    def _err(self, fail):
        try:
            result = self._failureTester(fail)
        except:
            self._deferred.errback()
        else:
            if self.failure is None:
                self.failure = fail
            if isinstance(result, failure.Failure):
                self._deferred.errback(result)
            else:
                log.msg('RetryingCall: Ignoring failure %s' % (fail,))
                self._call()

    def _call(self):
        try:
            delay = self._backoffIterator.next()
        except StopIteration:
            log.msg('StopIteration in RetryingCall: ran out of attempts.')
            self._deferred.errback(self.failure)
        else:
            d = task.deferLater(reactor, delay,
                                self._f, *self._args, **self._kw)
            d.addBoth(self._reportElapsed)
            d.addCallbacks(self._deferred.callback, self._err)

    def start(self, backoffIterator=None, failureTester=None):
        self._backoffIterator = iter(backoffIterator or simpleBackoffIterator())
        self._failureTester = failureTester or (lambda _: None)
        self._deferred = defer.Deferred()
        self.failure = None
        self._call()
        return self._deferred
