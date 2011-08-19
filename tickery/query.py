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

import ply.lex as lex
import ply.yacc as yacc
import re


class QueryError(Exception):
    pass


class UnparseableError(QueryError):
    pass


class TokenError(QueryError):

    def __init__(self, t):
        Exception.__init__(self)
        self.value = t.value
        self.offset = t.lexpos


class QueryLexer(object):

    # Ignore whitespace
    t_ignore = ' \t\n'

    tokens = (
        'SCREENNAME',
        'AND',
        'ANDSYM',
        'OR',
        'ORSYM',
        'LPAREN',
        'RPAREN',
        'EXCEPT',
        'EXCEPTSYM',
    )

    reserved = (u'and', u'or', u'except')

    t_LPAREN = '\('
    t_RPAREN = '\)'

    def t_EXCEPTSYM(self, t):
        r'-'
        t.value = 'except'
        return t

    def t_ORSYM(self, t):
        r'\|'
        t.value = 'or'
        return t

    def t_ANDSYM(self, t):
        r'&'
        t.value = 'and'
        return t

    def t_SCREENNAME(self, t):
        r'@?\w+'
        # The unicode conversions here probably aren't needed.
        lower = unicode(t.value.lower())
        if lower in self.reserved:
            t.type = t.value.upper()
        else:
            t.type = 'SCREENNAME'
            if t.value.startswith('@'):
                t.value = unicode(t.value[1:])
            else:
                t.value = unicode(t.value)
        return t

    def t_error(self, t):
        if isinstance(t, lex.LexToken):
            raise TokenError(t)
        else:
            raise Exception(t)

    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(reflags=re.UNICODE, object=self, **kwargs)


class Node(object):

    PAREN = 0
    BINOP = 1
    SCREENNAME = 2

    def __init__(self, type, left, right=None, detail=None):
        self.type = type
        self.left = left
        self.right = right
        self.detail = detail

    def __str__(self):
        if self.type == self.PAREN:
            assert self.right is None
            assert self.detail is None
            return '(' + str(self.left) + ')'
        elif self.type == self.BINOP:
            return '%s %s %s' % (str(self.left), self.detail, str(self.right))
        elif self.type == self.SCREENNAME:
            assert self.left is None
            assert self.right is None
            return self.detail
        else:
            raise Exception('WTF? Node type is %r' % (self.type,))


class QueryParser(object):

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EXCEPT'),
    )

    def __init__(self, tokens):
        self.tokens = tokens

    def p_query(self, p):
        '''query : screenname_query
                 | paren_query
                 | binop_query'''
        p[0] = p[1]

    def p_query_screenname(self, p):
        'screenname_query : SCREENNAME'
        p[0] = Node(Node.SCREENNAME, left=None, detail=p[1])

    def p_query_parens(self, p):
        'paren_query : LPAREN query RPAREN'
        p[0] = Node(Node.PAREN, p[2])

    def p_query_binop(self, p):
        '''binop_query : query OR query
                       | query ORSYM query
                       | query AND query
                       | query ANDSYM query
                       | query EXCEPT query
                       | query EXCEPTSYM query'''
        p[0] = Node(Node.BINOP, left=p[1], right=p[3], detail=p[2])

    def p_error(self, p):
        if isinstance(p, lex.LexToken):
            raise TokenError(p)
        else:
            raise UnparseableError(p)

    def build(self, **kwargs):
        self.yacc = yacc.yacc(**kwargs)

    def parse(self, query, lexer):
        return self.yacc.parse(input=query, lexer=lexer)


class ASTBuilder(object):
    def __init__(self):
        self.lexer = QueryLexer()
        self.lexer.build()
        self.parser = QueryParser(self.lexer.tokens)
        self.parser.build(module=self.parser, debug=False, outputdir='.')

    def build(self, query):
        try:
            return self.parser.parse(query, self.lexer.lexer)
        except RuntimeError:
            raise UnparseableError()


def queryTreeToString(queryTree, fdbUsername, fdbNamespace):
    """Return a query string that can be sent to Fluidinfo. Note that we turn
    all screennames into lowercase in the complete tag names. That's
    because that's the way we create the tags.
    """
    nodeType = queryTree.type
    if nodeType == Node.PAREN:
        assert queryTree.right is None
        assert queryTree.detail is None
        return u'(%s)' % queryTreeToString(
            queryTree.left, fdbUsername, fdbNamespace)
    elif nodeType == Node.BINOP:
        return u'%s %s %s' % (
            queryTreeToString(queryTree.left, fdbUsername, fdbNamespace),
            queryTree.detail,
            queryTreeToString(queryTree.right, fdbUsername, fdbNamespace))
    elif nodeType == Node.SCREENNAME:
        assert queryTree.left is None
        assert queryTree.right is None
        screenname = queryTree.detail
        return u'has ' + u'/'.join(
            [fdbUsername, fdbNamespace, screenname.lower()])
    else:
        raise Exception('WTF? Node type is %r' % (nodeType,))


def queryTreeExtractScreennames(queryTree, screennames):
    """Pull all the screennames out of a query tree. Do this in a
    case-insensitive way. Return a set of names that preserves case (first
    casing found wins).
    """
    nodeType = queryTree.type
    if nodeType == Node.PAREN:
        queryTreeExtractScreennames(queryTree.left, screennames)
    elif nodeType == Node.BINOP:
        queryTreeExtractScreennames(queryTree.left, screennames)
        queryTreeExtractScreennames(queryTree.right, screennames)
    elif nodeType == Node.SCREENNAME:
        screenname = queryTree.detail
        if screenname.lower() not in screennames:
            screennames.add(screenname)
    else:
        raise Exception('WTF? Node type is %r' % (nodeType,))
