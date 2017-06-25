#!/usr/bin/env python
# -*- encoding: utf-8 -*-

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


import json
from os.path import dirname, join as path_join
from unittest import TestCase

import pygments
from pygments.token import Whitespace, Keyword, Operator, Name

from cypy.lex import CypherLexer, cypher_keywords, cypher_pseudo_keywords, cypher_operator_words, \
    cypher_operator_symbols


class LexerTestCase(TestCase):

    lexer = CypherLexer()

    def test_statements_in_test_file(self):
        with open(path_join(dirname(__file__), "files", "lex", "lexer-test.json")) as f:
            for x in json.load(f):
                code = x["code"]
                expected_tokens = x["tokens"]
                actual_tokens = [t[-1] for t, _ in pygments.lex(code, self.lexer) if t is not Whitespace]
                self.assertEqual(expected_tokens, actual_tokens, msg="Token mismatch when parsing {!r}".format(code))

    def test_all_keywords(self):
        for word in cypher_keywords:
            expected_tokens = [(Keyword, word)]
            actual_tokens = [t for t in pygments.lex(word, self.lexer) if t[0] is not Whitespace]
            self.assertEqual(expected_tokens, actual_tokens, msg="Token mismatch when parsing {!r}".format(word))

    def test_all_pseudo_keywords(self):
        for word in cypher_pseudo_keywords:
            expected_tokens = [(Keyword, word)]
            actual_tokens = [t for t in pygments.lex(word, self.lexer) if t[0] is not Whitespace]
            self.assertEqual(expected_tokens, actual_tokens, msg="Token mismatch when parsing {!r}".format(word))

    def test_all_operators(self):
        for op in cypher_operator_words + cypher_operator_symbols:
            expected_tokens = [(Name.Variable, "x"), (Operator, op), (Name.Variable, "y")]
            actual_tokens = [t for t in pygments.lex("x {} y".format(op), self.lexer) if t[0] is not Whitespace]
            self.assertEqual(expected_tokens, actual_tokens, msg="Token mismatch when parsing {!r}".format(op))

    def test_all_operator_symbols_without_spaces(self):
        for op in cypher_operator_symbols:
            expected_tokens = [(Name.Variable, "x"), (Operator, op), (Name.Variable, "y")]
            actual_tokens = [t for t in pygments.lex("x{}y".format(op), self.lexer) if t[0] is not Whitespace]
            self.assertEqual(expected_tokens, actual_tokens, msg="Token mismatch when parsing {!r}".format(op))


class LexerStatementSplittingTestCase(TestCase):

    lexer = CypherLexer()

    def test_can_get_single_statement(self):
        statements = list(self.lexer.get_statements("RETURN 1"))
        self.assertEqual(statements, ["RETURN 1"])

    def test_can_get_multiple_statements(self):
        statements = list(self.lexer.get_statements("RETURN 1; RETURN 2; RETURN 3"))
        self.assertEqual(statements, ["RETURN 1", "RETURN 2", "RETURN 3"])

    def test_whitespace_is_ignored(self):
        statements = list(self.lexer.get_statements("   RETURN 1\t;\tRETURN 2;\r\n     RETURN 3 "))
        self.assertEqual(statements, ["RETURN 1", "RETURN 2", "RETURN 3"])

    def test_empty_statements_are_ignored(self):
        statements = list(self.lexer.get_statements("RETURN 1; RETURN 2;; RETURN 3;;;"))
        self.assertEqual(statements, ["RETURN 1", "RETURN 2", "RETURN 3"])
