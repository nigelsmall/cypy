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


from unittest import TestCase

from cypy.data.subgraph import Subgraph, Node, Relationship, Path

a = Node("Person", name="Alice")
b = Node("Person", name="Bob")
c = Node("Person", name="Carol")
d = Node("Person", name="Dave")
e = Node("Person", name="Eve")
ab = Relationship(a, "KNOWS", b)
bc = Relationship(b, "KNOWS", c)
dc = Relationship(d, "KNOWS", c)
de = Relationship(d, "KNOWS", e)


class PathTestCase(TestCase):

    def test_can_build_path_from_single_node(self):
        p = Path(a)
        self.assertEqual(p.nodes(), (a,))
        self.assertEqual(p.relationships(), ())

    def test_can_build_path_from_two_identical_nodes(self):
        p = Path(a, a)
        self.assertEqual(p.nodes(), (a,))
        self.assertEqual(p.relationships(), ())

    def test_cannot_build_path_from_two_different_nodes(self):
        with self.assertRaises(ValueError):
            _ = Path(a, b)

    def test_can_build_path_from_single_relationship(self):
        p = Path(ab)
        self.assertEqual(p.nodes(), (a, b))
        self.assertEqual(p.relationships(), (ab,))

    def test_can_build_path_from_two_relationships(self):
        p = Path(ab, bc)
        self.assertEqual(p.nodes(), (a, b, c))
        self.assertEqual(p.relationships(), (ab, bc))

    def test_can_build_path_with_reversed_relationship(self):
        p = Path(bc, dc)
        self.assertEqual(p.nodes(), (b, c, d))
        self.assertEqual(p.relationships(), (bc, dc))

    def test_can_build_path_with_initial_reversed_relationship(self):
        p = Path(dc, de)
        self.assertEqual(p.nodes(), (c, d, e))
        self.assertEqual(p.relationships(), (dc, de))

    def test_can_build_path_from_multiple_relationships(self):
        p = Path(ab, bc, dc, de)
        self.assertEqual(p.nodes(), (a, b, c, d, e))
        self.assertEqual(p.relationships(), (ab, bc, dc, de))

    def test_can_build_path_from_various_combinations(self):
        node_sets = [
            [None, None, None],
            [a, None, None],
            [a, b, None],
            [None, b, None],
            [None, b, c],
            [None, None, c],
            [a, None, c],
            [a, b, c],
        ]
        r = [ab, bc]
        for n in node_sets:
            entities = [entity for entity in [n[0], r[0], n[1], r[1], n[2]] if entity is not None]
            p = Path(*entities)
            self.assertEqual(p.nodes(), (a, b, c))
            self.assertEqual(p.relationships(), (ab, bc))

    def test_subgraph_from_path(self):
        p = Path(ab, bc, dc, de)
        s = Subgraph(p)
        self.assertEqual(set(s.nodes()), {a, b, c, d, e})
        self.assertEqual(set(s.relationships()), {ab, bc, dc, de})
