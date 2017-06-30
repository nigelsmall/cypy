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


from unittest import TestCase

from cypy.data import Node
from cypy.encoding import cypher_repr


class ReprTestCase(TestCase):

    def test_empty_node(self):
        a = Node()
        r = cypher_repr(a, node_template="{labels} {properties}")
        self.assertEqual(u"({})", r)

    def test_node_with_label(self):
        a = Node("Person")
        r = cypher_repr(a, node_template="{labels} {properties}")
        self.assertEqual(u"(:Person {})", r)

    def test_node_with_multiple_labels(self):
        a = Node("Person", "Employee")
        r = cypher_repr(a, node_template="{labels} {properties}")
        self.assertEqual(u"(:Employee:Person {})", r)

    def test_node_with_labels_and_properties(self):
        a = Node("Person", name="Alice")
        r = cypher_repr(a, node_template="{labels} {properties}")
        self.assertEqual(u"(:Person {name: 'Alice'})", r)

    def test_node_with_only_properties(self):
        a = Node(name="Alice", age=33)
        r = cypher_repr(a, node_template="{labels} {properties}")
        self.assertEqual(u"({age: 33, name: 'Alice'})", r)
