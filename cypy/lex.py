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

from pygments.lexer import RegexLexer, include, bygroups
from pygments.token import Keyword, Punctuation, Comment, Operator, Name, \
    String, Number, Whitespace


__all__ = ["cypher_keywords", "CypherLexer"]


cypher_keywords = [
    "AS",
    "ASC",
    "ASCENDING",
    "ASSERT",
    "CALL",
    "CREATE",
    "CREATE CONSTRAINT ON",
    "CREATE INDEX ON",
    "CREATE UNIQUE",
    "DELETE",
    "DESC",
    "DESCENDING",
    "DETACH DELETE",
    "DROP CONSTRAINT ON",
    "DROP INDEX ON",
    "EXPLAIN",
    "FIELDTERMINATOR",
    "FOREACH",
    "FROM",
    "LIMIT",
    "LOAD CSV",
    "MATCH",
    "MERGE",
    "ON CREATE SET",
    "ON MATCH SET",
    "OPTIONAL MATCH",
    "ORDER BY",
    "PROFILE",
    "REMOVE",
    "RETURN",
    "RETURN DISTINCT",
    "SET",
    "SKIP",
    "START",
    "UNION",
    "UNION ALL",
    "UNWIND",
    "USING INDEX",
    "USING JOIN ON",
    "USING PERIODIC COMMIT",
    "USING SCAN",
    "WHERE",
    "WITH",
    "WITH DISTINCT",
    "WITH HEADERS",
    "YIELD",
]
cypher_pseudo_keywords = [
    "BEGIN"
    "COMMIT",
    "ROLLBACK",
]
cypher_operator_symbols = [
    "!=",
    "%",
    "*",
    "+",
    "+=",
    "-",
    ".",
    "/",
    "<",
    "<=",
    "<>",
    "=",
    "=~",
    ">",
    ">=",
    "^",
]
cypher_operator_words = [
    'AND',
    'CASE',
    'CONTAINS',
    'DISTINCT',
    'ELSE',
    'END',
    'ENDS WITH',
    'IN',
    'IS NOT NULL',
    'IS NULL',
    'NOT',
    'OR',
    'STARTS WITH',
    'THEN',
    'WHEN',
    'XOR',
]
cypher_constants = [
    'null',
    'true',
    'false',
]


def word_list(words, token_type):
    return list(reversed(sorted((word.replace(" ", r"\s+") + r"\b", token_type) for word in words)))


def symbol_list(symbols, token_type):
    return list(reversed(sorted(("".join("\\" + ch for ch in symbol), token_type) for symbol in symbols)))


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
            include('pseudo-keywords'),
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

        'keywords': word_list(cypher_keywords, Keyword),
        'pseudo-keywords': word_list(cypher_pseudo_keywords, Keyword),

        'labels': [
            (r'(:)(\s*)(`(?:``|[^`])+`)', bygroups(Punctuation, Whitespace, Name.Label)),
            (r'(:)(\s*)([A-Za-z_][0-9A-Za-z_]*)', bygroups(Punctuation, Whitespace, Name.Label)),
        ],

        'operators': (word_list(cypher_operator_words, Operator) +
                      symbol_list(cypher_operator_symbols, Operator)),

        'expressions': [
            include('callables'),
            include('constants'),
            include('aliases'),
            include('variables'),
            include('parameters'),
            include('numbers'),
        ],
        'callables': [
            # procedures
            (r'(CALL)(\s+)([A-Za-z_][0-9A-Za-z_\.]*)', bygroups(Keyword, Whitespace, Name.Function)),
            # functions
            (r'([A-Za-z_][0-9A-Za-z_\.]*)(\s*)(\()', bygroups(Name.Function, Whitespace, Punctuation), "in-()"),
        ],
        'aliases': [
            (r'(AS)(\s+)(`(?:``|[^`])+`)', bygroups(Keyword, Whitespace, Name.Variable)),
            (r'(AS)(\s+)([A-Za-z_][0-9A-Za-z_]*)', bygroups(Keyword, Whitespace, Name.Variable)),
        ],
        'variables': [
            (r'`(?:``|[^`])+`', Name.Variable),
            (r'[A-Za-z_][0-9A-Za-z_]*', Name.Variable),
        ],
        'parameters': [
            (r'(\$)(`(?:``|[^`])+`)', bygroups(Punctuation, Name.Variable.Global)),
            (r'(\$)([A-Za-z_][0-9A-Za-z_]*)', bygroups(Punctuation, Name.Variable.Global)),
        ],
        'constants': word_list(cypher_constants, Name.Constant),
        'numbers': [
            (r'[0-9]*\.[0-9]*(e[+-]?[0-9]+)?', Number.Float),
            (r'[0-9]+e[+-]?[0-9]+', Number.Float),
            (r'[0-9]+', Number.Integer),
        ],

        'whitespace': [
            (r'\s+', Whitespace),
        ],

    }
