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

from neo4j.v1 import Node, Relationship, Path

from cypy.encoding import cypher_repr


class CypherNodeRepresentationTestCase(TestCase):

    def test_should_encode_empty_node(self):
        a = Node()
        a.id = 1
        encoded = cypher_repr(a)
        self.assertEqual(u"(#1 {})", encoded)

    def test_should_encode_node_with_property(self):
        a = Node([], {"name": "Alice"})
        a.id = 1
        encoded = cypher_repr(a)
        self.assertEqual(u"(#1 {name: 'Alice'})", encoded)

    def test_should_encode_node_with_label(self):
        a = Node(["Person"])
        a.id = 1
        encoded = cypher_repr(a)
        self.assertEqual(u"(#1:Person {})", encoded)

    def test_should_encode_node_with_label_and_property(self):
        a = Node(["Person"], {"name": "Alice"})
        a.id = 1
        encoded = cypher_repr(a)
        self.assertEqual(u"(#1:Person {name: 'Alice'})", encoded)


class CypherRelationshipRepresentationTestCase(TestCase):

    def test_can_encode_relationship(self):
        a = Node()
        a.id = 1
        b = Node()
        b.id = 2
        ab = Relationship(a, b, "TO")
        encoded = cypher_repr(ab)
        self.assertEqual("(#1)-[:TO {}]->(#2)", encoded)

    def test_can_encode_relationship_with_numeric_endpoints(self):
        ab = Relationship(1, 2, "TO")
        encoded = cypher_repr(ab)
        self.assertEqual("(#1)-[:TO {}]->(#2)", encoded)

    def test_can_encode_relationship_with_names(self):
        a = Node(["Person"], {"name": "Alice"})
        a.id = 1
        b = Node(["Person"], {"name": "Bob"})
        b.id = 2
        ab = Relationship(a, b, "KNOWS")
        encoded = cypher_repr(ab)
        self.assertEqual("(#1)-[:KNOWS {}]->(#2)", encoded)

    def test_can_encode_relationship_with_alternative_names(self):
        a = Node(["Person"], {"nom": u"Aimée"})
        a.id = 1
        b = Node(["Person"], {"nom": u"Baptiste"})
        b.id = 2
        ab = Relationship(a, b, u"CONNAÎT")
        encoded = cypher_repr(ab, related_node_template=u"{property.nom}")
        self.assertEqual(u"(Aimée)-[:CONNAÎT {}]->(Baptiste)", encoded)

    def test_can_encode_relationship_with_properties(self):
        a = Node(["Person"], {"name": "Alice"})
        a.id = 1
        b = Node(["Person"], {"name": "Bob"})
        b.id = 2
        ab = Relationship(a, b, "KNOWS", since=1999)
        encoded = cypher_repr(ab)
        self.assertEqual("(#1)-[:KNOWS {since: 1999}]->(#2)", encoded)


class CypherPathRepresentationTestCase(TestCase):

    def test_can_write_path(self):
        alice, bob, carol, dave = Node([], {"name": "Alice"}), Node([], {"name": "Bob"}), \
                                  Node([], {"name": "Carol"}), Node([], {"name": "Dave"})
        alice.id = 1
        bob.id = 2
        carol.id = 3
        dave.id = 4
        ab = Relationship(alice, bob, "LOVES")
        cb = Relationship(carol, bob, "HATES")
        cd = Relationship(carol, dave, "KNOWS")
        path = Path(alice, ab, bob, cb, carol, cd, dave)
        encoded = cypher_repr(path)
        self.assertEqual("(#1)-[:LOVES {}]->(#2)<-[:HATES {}]-(#3)-[:KNOWS {}]->(#4)", encoded)
