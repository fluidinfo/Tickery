from operator import add, mul
from functools import partial

from twisted.trial import unittest
from twisted.python import log
from twisted.internet import defer

from tickery.looper import simpleBackoffIterator, RetryingCall


class TestBackoffIterator(unittest.TestCase):
    def testNow(self):
        bi = simpleBackoffIterator(now=True, initDelay=9)
        delay = bi.next()
        self.assertEqual(0.0, delay)
        
    def testNotNow(self):
        bi = simpleBackoffIterator(now=False, initDelay=3.0)
        delay = bi.next()
        self.assertNotEqual(0.0, delay)
        
    def testInitDelay(self):
        initDelay = 7
        bi = simpleBackoffIterator(now=False, initDelay=initDelay,
                                   maxDelay=initDelay + 1)
        delay = bi.next()
        self.assertEqual(initDelay, delay)
        
    def testDefaultSettingsEventuallyHalt(self):
        bi = simpleBackoffIterator()
        for delay in bi:
            pass
        
    def testDefaultSettingsNoNegativeDelays(self):
        bi = simpleBackoffIterator()
        for delay in bi:
            self.assertTrue(delay >= 0.0)
        
    def testMaxResults(self):
        maxResults = 12
        bi = simpleBackoffIterator(now=False, maxResults=maxResults)
        for _ in range(maxResults):
            bi.next()
        self.assertRaises(StopIteration, bi.next)
        
    def testConstant(self):
        n = 10
        constant = 5.0
        initDelay = 3.0
        bi = simpleBackoffIterator(now=False,
                                   initDelay=initDelay,
                                   incFunc=lambda _: constant,
                                   maxDelay=10.0,
                                   maxResults=n + 1)
        self.assertEqual(initDelay, bi.next())
        for _ in range(n):
            self.assertEqual(constant, bi.next())

    def testMul2(self):
        bi = simpleBackoffIterator(now=False,
                                   initDelay=1.0,
                                   incFunc=partial(mul, 2.0),
                                   maxDelay=10.0,
                                   maxResults=10)
        self.assertEqual(1.0, bi.next())
        self.assertEqual(2.0, bi.next())
        self.assertEqual(4.0, bi.next())

    def testAdd3(self):
        bi = simpleBackoffIterator(now=False,
                                   initDelay=2.0,
                                   incFunc=partial(add, 3.0),
                                   maxDelay=10.0,
                                   maxResults=10)
        self.assertEqual(2.0, bi.next())
        self.assertEqual(5.0, bi.next())
        self.assertEqual(8.0, bi.next())


class InitiallyFailing(object):
    """Provide a callable that raises for its first nFails calls, then
    returns the passed result."""
    def __init__(self, nFails, result=None, exceptionList=None, *args, **kw):
        assert nFails >= 0
        self.nFails = nFails
        self.result = result
        self.exceptionList = exceptionList or []
        self.args = args
        self.kw = kw
        self.failCount = 0
        self.succeeded = False

    def __call__(self, *args, **kw):
        # Make sure we're called with the args we're supposed to be called with.
        assert self.args == args
        assert self.kw == kw
        
        if self.failCount < self.nFails:
            try:
                excClass = self.exceptionList[self.failCount]
            except IndexError:
                log.msg('Ran out of exceptions, raising a generic Exception')
                excClass = Exception
            self.failCount += 1
            raise excClass()
        else:
            # Make sure we only succeed once.
            assert self.succeeded is False
            self.succeeded = True
            return self.result

    def assertMaximallyFailed(self):
        assert self.nFails == self.failCount, '%d != %d' % (self.nFails,
                                                            self.failCount)

class CallCounter(object):
    """Provide a callable that counts the number of times it's invoked."""
    def __init__(self):
        self.nCalls = 0

    def __call__(self, value):
        self.nCalls += 1
        return value

    def assertCalledOnce(self):
        assert self.nCalls == 1


class ValueErrorThenNameErrorRaiser(object):
    """Provide a callable that raises a ValueError on its first invocation
    and a NameError thereafter."""
    def __init__(self):
        self.called = False

    def __call__(self):
        if self.called:
            raise NameError()
        else:
            self.called = True
            raise ValueError()
        

class TestRetryingCall(unittest.TestCase):
    def testSimplestNoFailure(self):
        result = 15
        rc = RetryingCall(lambda: result)
        d = rc.start()
        d.addCallback(lambda r: self.assertEqual(r, result))
        return d
    
    def testSimplestDeferredReturner(self):
        result = 15
        rc = RetryingCall(lambda: defer.succeed(result))
        d = rc.start()
        d.addCallback(lambda r: self.assertEqual(r, result))
        return d
    
    def testSimpleDeferredReturner(self):
        result1 = 15
        result2 = 16
        def _ret(result):
            self.assertEqual(result, result1)
            return result2
        rc = RetryingCall(lambda: defer.succeed(result1))
        d = rc.start()
        d.addCallback(_ret)
        d.addCallback(lambda r: self.assertEqual(r, result2))
        return d
    
    def testInitiallyFailing0Failures(self):
        f = InitiallyFailing(0)
        rc = RetryingCall(f)
        d = rc.start()
        d.addCallback(lambda _: f.assertMaximallyFailed())
        return d

    def testSimpleArgs(self):
        result = 9
        rc = RetryingCall(lambda x: x, result)
        d = rc.start()
        d.addCallback(lambda r: self.assertEqual(r, result))
        return d

    def testSimpleKwArgs(self):
        result = 9
        rc = RetryingCall(lambda xxx=None: xxx, xxx=result)
        d = rc.start()
        d.addCallback(lambda r: self.assertEqual(r, result))
        return d

    def testSimpleArgAndKwArg(self):
        x = 9
        y = 'hey'
        rc = RetryingCall(lambda x, y=None: (x, y), x, y=y)
        d = rc.start()
        d.addCallback(lambda r: self.assertEqual(r, (x, y)))
        return d
    
    def testIgnoreRegularException(self):
        def _failureTester(f):
            f.trap(Exception)
        result = 5
        f = InitiallyFailing(3, result=result)
        rc = RetryingCall(f)
        d = rc.start(failureTester=_failureTester)
        d.addCallback(lambda r: self.assertEqual(r, result))
        d.addCallback(lambda _: f.assertMaximallyFailed())
        return d

    def test1ValueError(self):
        def _failureTester(f):
            f.trap(ValueError)
        result = 5
        f = InitiallyFailing(1, result=result, exceptionList=[ValueError])
        rc = RetryingCall(f)
        d = rc.start(failureTester=_failureTester)
        d.addCallback(lambda r: self.assertEqual(r, result))
        d.addCallback(lambda _: f.assertMaximallyFailed())
        return d

    def test3ValueErrors(self):
        def _failureTester(f):
            f.trap(ValueError)
        result = 5
        nExceptions = 3
        f = InitiallyFailing(nExceptions, result=result,
                             exceptionList=[ValueError] * nExceptions)
        rc = RetryingCall(f)
        d = rc.start(failureTester=_failureTester)
        d.addCallback(lambda r: self.assertEqual(r, result))
        d.addCallback(lambda _: f.assertMaximallyFailed())
        return d

    def testDontAllowKeyError(self):
        def _failureTester(f):
            f.trap(ValueError)
        f = InitiallyFailing(3, exceptionList=[KeyError])
        rc = RetryingCall(f)
        d = rc.start(failureTester=_failureTester)
        self.failUnlessFailure(d, KeyError)
        return d

    def testValueErrorThenNameError(self):
        def _failureTester(f):
            if not f.check(ValueError, NameError):
                return f
        result = 15
        f = InitiallyFailing(2, result=result,
                             exceptionList=[ValueError, NameError])
        rc = RetryingCall(f)
        d = rc.start(failureTester=_failureTester)
        d.addCallback(lambda r: self.assertEqual(r, result))
        d.addCallback(lambda _: f.assertMaximallyFailed())
        return d

    def testListBackoffIteratorAsList(self):
        rc = RetryingCall(lambda: defer.fail(Exception()))
        d = rc.start(backoffIterator=[0.05, 0.06, 0.07])
        self.failUnlessFailure(d, Exception)
        return d

    def testListBackoffIteratorAsTuple(self):
        rc = RetryingCall(lambda: defer.fail(Exception()))
        d = rc.start(backoffIterator=(0.01, 0.01, 0.01))
        self.failUnlessFailure(d, Exception)
        return d

    def testExactlyOneSuccessfulCall(self):
        result = 99
        f = CallCounter()
        rc = RetryingCall(f, result)
        d = rc.start()
        d.addCallback(lambda r: self.assertEqual(r, result))
        d.addCallback(lambda _: f.assertCalledOnce())
        return d

    def testFirstFailureReceived(self):
        f = ValueErrorThenNameErrorRaiser()
        rc = RetryingCall(f)
        d = rc.start(backoffIterator=(0.01, 0.01, 0.01))
        self.failUnlessFailure(d, ValueError)
        return d
