#!/usr/bin/env python
# coding: utf-8

# Copyright 2011-2017, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Pygments lexer for Cypher.
"""

import re

from pygments.lexer import RegexLexer, include, words, bygroups
from pygments.token import Keyword, Punctuation, Comment, Operator, Name, \
    String, Number, Whitespace

__all__ = ['CypherLexer']


class CypherLexer(RegexLexer):
    """
    For `Cypher Query Language
    <https://neo4j.com/docs/cypher-refcard/current/>`_

    For the Cypher version in Neo4j 3.2
    """
    name = 'Cypher'
    aliases = ['cypher']
    filenames = ['*.cypher', '*.cyp']

    flags = re.IGNORECASE | re.MULTILINE | re.UNICODE

    tokens = {

        'root': [
            include('strings'),
            include('comments'),
            include('keywords'),
            (r'[,;]', Punctuation),
            include('labels'),
            include('operators'),
            include('expressions'),
            include('whitespace'),
            (r'\(', Punctuation, 'in-()'),
            (r'\[', Punctuation, 'in-[]'),
            (r'\{', Punctuation, 'in-{}'),
        ],
        'in-()': [
            include('strings'),
            include('comments'),
            include('keywords'),        # keywords used in FOREACH
            (r'[,;|]', Punctuation),
            include('labels'),
            include('operators'),
            include('expressions'),
            include('whitespace'),
            (r'\(', Punctuation, '#push'),
            (r'\)\s*<?-+>?\s*\(', Punctuation),
            (r'\)\s*<?-+\s*\[', Punctuation, ('#pop', 'in-[]')),
            (r'\)', Punctuation, '#pop'),
            (r'\[', Punctuation, 'in-[]'),
            (r'\{', Punctuation, 'in-{}'),
        ],
        'in-[]': [
            include('strings'),
            include('comments'),
            (r'WHERE\b', Keyword),      # used in list comprehensions
            (r'[,;|]', Punctuation),
            include('labels'),
            include('operators'),
            include('expressions'),
            include('whitespace'),
            (r'\(', Punctuation, 'in-()'),
            (r'\[', Punctuation, '#push'),
            (r'\]\s*-+>?\s*\(', Punctuation, ('#pop', 'in-()')),
            (r'\]', Punctuation, '#pop'),
            (r'\{', Punctuation, 'in-{}'),
        ],
        'in-{}': [
            include('strings'),
            include('comments'),
            (r'[,:;]', Punctuation),
            include('operators'),
            include('expressions'),
            include('whitespace'),
            (r'\(', Punctuation, 'in-()'),
            (r'\[', Punctuation, 'in-[]'),
            (r'\{', Punctuation, '#push'),
            (r'\}', Punctuation, '#pop'),
        ],

        'comments': [
            (r'^.*//.*\n', Comment.Single),
            (r'/\*', Comment.Multiline, 'multiline-comments'),
        ],
        'multiline-comments': [
            (r'/\*', Comment.Multiline, 'multiline-comments'),
            (r'\*/', Comment.Multiline, '#pop'),
            (r'[^/*]+', Comment.Multiline),
            (r'[/*]', Comment.Multiline)
        ],

        'strings': [
            # TODO: highlight escape sequences
            (r"'(?:\\[bfnrt\"'\\]|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8}|[^\\'])*'", String),
            (r'"(?:\\[bfnrt\'"\\]|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8}|[^\\"])*"', String),
        ],

        'keywords': [
            (r'CREATE\s+UNIQUE\b', Keyword),
            (r'CREATE\s+CONSTRAINT\s+ON\b', Keyword),
            (r'CREATE\s+INDEX\s+ON\b', Keyword),
            (r'DETACH\s+DELETE\b', Keyword),
            (r'DROP\s+CONSTRAINT\s+ON\b', Keyword),
            (r'DROP\s+INDEX\s+ON\b', Keyword),
            (r'LOAD\s+CSV\b', Keyword),
            (r'OPTIONAL\s+MATCH\b', Keyword),
            (r'ON\s+CREATE\s+SET\b', Keyword),
            (r'ON\s+MATCH\s+SET\b', Keyword),
            (r'ORDER\s+BY\b', Keyword),
            (r'RETURN\s+DISTINCT\b', Keyword),
            (r'UNION\s+ALL\b', Keyword),
            (r'USING\s+INDEX\b', Keyword),
            (r'USING\s+JOIN\s+ON\b', Keyword),
            (r'USING\s+PERIODIC\s+COMMIT\b', Keyword),
            (r'USING\s+SCAN\b', Keyword),
            (r'WITH\s+DISTINCT\b', Keyword),
            (r'WITH\s+HEADERS\b', Keyword),
            (words((
                'ASC',
                'ASCENDING',
                'ASSERT',
                'CREATE',
                'DELETE',
                'DESC',
                'DESCENDING',
                'EXPLAIN',
                'FIELDTERMINATOR',
                'FOREACH',
                'FROM',
                'LIMIT',
                'MATCH',
                'MERGE',
                'PROFILE',
                'REMOVE',
                'RETURN',
                'SET',
                'SKIP',
                'START',
                'UNION',
                'UNWIND',
                'WHERE',
                'WITH',
                'YIELD',
            ), suffix=r'\b'), Keyword),
            (words((
                'BEGIN',
                'COMMIT',
                'ROLLBACK',
            ), suffix=r'\b'), Keyword.Pseudo),
        ],

        'labels': [
            (r'(:)(\s*)(`(?:``|[^`])+`)', bygroups(Punctuation, Whitespace, Name.Label)),
            (r'(:)(\s*)([A-Za-z_][0-9A-Za-z_]*)', bygroups(Punctuation, Whitespace, Name.Label)),
        ],

        'operators': [
            (r'ENDS\s+WITH\b', Operator),
            (r'IS\s+NOT\s+NULL\b', Operator),
            (r'IS\s+NULL\b', Operator),
            (r'STARTS\s+WITH\b', Operator),
            (words((
                'AND',
                'CASE',
                'CONTAINS',
                'DISTINCT',
                'ELSE',
                'END',
                'IN',
                'NOT',
                'OR',
                'THEN',
                'WHEN',
                'XOR',
            ), suffix=r'\b'), Operator),
            (r'\+=', Operator),
            (r'=~', Operator),
            (r'=|<>|!=|<|>|<=|>=', Operator),
            (r'[\+\-\*/%^\.]', Operator),
        ],

        'expressions': [
            include('callables'),
            include('identifiers'),
            include('constants'),
            include('numbers'),
        ],
        'callables': [
            # procedures
            (r'(CALL)(\s+)([A-Za-z_][0-9A-Za-z_\.]*)', bygroups(Keyword, Whitespace, Name.Function)),
            # functions
            (r'([A-Za-z_][0-9A-Za-z_\.]*)(\s*)(\()', bygroups(Name.Function, Whitespace, Punctuation), "in-()"),
        ],
        'identifiers': [
            # aliases
            (r'(AS)(\s+)(`(?:``|[^`])+`)', bygroups(Keyword, Whitespace, Name.Variable)),
            (r'(AS)(\s+)([A-Za-z_][0-9A-Za-z_]*)', bygroups(Keyword, Whitespace, Name.Variable)),
            # variables
            (r'`(?:``|[^`])+`', Name.Variable),
            (r'[A-Za-z_][0-9A-Za-z_]*', Name.Variable),
            # parameters
            (r'(\$)(`(?:``|[^`])+`)', bygroups(Punctuation, Name.Variable.Global)),
            (r'(\$)([A-Za-z_][0-9A-Za-z_]*)', bygroups(Punctuation, Name.Variable.Global)),
        ],
        'constants': [
            (words((
                'null',
                'true',
                'false'
            ), suffix=r'\b'), Name.Constant),
        ],
        'numbers': [
            (r'([0-9]*\.[0-9]*|[0-9]+)(e[+-]?[0-9]+)?', Number.Float),
            (r'[0-9]+', Number.Integer),
        ],

        'whitespace': [
            (r'\s+', Whitespace),
        ],

    }
