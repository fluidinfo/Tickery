from twisted.trial import unittest
from twisted.python import log

from tickery.query import ASTBuilder, TokenError, UnparseableError


class TestParse(unittest.TestCase):
    def setUp(self):
        self.ast = ASTBuilder()

    def _simpleCorrectCheck(self, query):
        try:
            p = self.ast.build(query)
        except TokenError, t:
            log.err('Token error on query %r: text=%r, offset=%d' %
                    (query, t.value, t.offset))
            raise
        except Exception:
            log.err('Exception with expected correct query %r' % query)
            raise
        else:
            q = query.replace('&', 'and').replace('|', 'or').\
                replace('-', 'except').replace('@', '')
            self.assertEqual(str(p), q)

    def _simpleTokenErrorCheck(self, query, value, offset):
        try:
            p = self.ast.build(query)
        except TokenError, p:
            self.assertTrue(p.value.startswith(value))
            self.assertEqual(p.offset, offset)
        else:
            self.fail('Expected a ParseError on %r at offset %d in %r. Got %r'
                      % (value, offset, query, p))

    def _simpleUnparseableCheck(self, query):
        try:
            self.ast.build(query)
        except UnparseableError:
            pass
        else:
            self.fail('Expected an UnparseableError on query %r.' % query)

    def testSimpleCorrectQueries(self):
        for q in ('romeo',
                  '@juliet',
                  '@and and @and',
                  '@and & @and',
                  '@or or @or',
                  '@or | @or',
                  '@except except @except',
                  '@except - @except',
                  'romeo & juliet',
                  'romeo and juliet',
                  'romeo & juliet & malvolio',
                  'romeo & juliet and malvolio',
                  '(romeo & juliet) & malvolio',
                  '(romeo and juliet) & malvolio',
                  '(romeo | juliet) & malvolio',
                  '(romeo or juliet) or malvolio',
                  'romeo and @juliet'):
            self._simpleCorrectCheck(q)

    def testSimpleTokenErrors(self):
        for query, value, offset in (
            (')', ')', 0),
            ('()', ')', 1),
            ('(xxx=)', '=', 4),
            ('(xxx=yyy)', '=', 4),
            ):
            self._simpleTokenErrorCheck(query, value, offset)

    def testSimpleUnparseableErrors(self):
        for query in ('',
                      '(',
                      ):
            self._simpleUnparseableCheck(query)
