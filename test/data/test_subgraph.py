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

from cypy.data import Subgraph, Node, Relationship


class SubgraphTestCase(TestCase):

    def test_should_be_able_to_create_empty_subgraph(self):
        s = Subgraph()
        assert s.order() == 0
        assert s.size() == 0
        assert set(s.nodes()) == set()
        assert set(s.relationships()) == set()

    def test_should_be_able_to_create_subgraph_from_single_node(self):
        a = Node(name="Alice")
        s = Subgraph(a)
        assert s.order() == 1
        assert s.size() == 0
        assert set(s.nodes()) == {a}
        assert set(s.relationships()) == set()

    def test_should_be_able_to_create_subgraph_from_union_of_nodes(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        s = Subgraph.union(a, b)
        assert s.order() == 2
        assert s.size() == 0
        assert set(s.nodes()) == {a, b}
        assert set(s.relationships()) == set()

    def test_should_be_able_to_create_subgraph_from_union_of_nodes_using_operator(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        s = a | b
        assert s.order() == 2
        assert s.size() == 0
        assert set(s.nodes()) == {a, b}
        assert set(s.relationships()) == set()

    def test_should_be_able_to_create_subgraph_from_union_of_relationships(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        c = Node(name="Carol")
        ab = Relationship(a, "KNOWS", b)
        bc = Relationship(b, "KNOWS", c)
        s = Subgraph.union(ab, bc)
        assert s.order() == 3
        assert s.size() == 2
        assert set(s.nodes()) == {a, b, c}
        assert set(s.relationships()) == {ab, bc}

    def test_should_be_able_to_create_subgraph_from_union_of_relationships_using_operator(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        c = Node(name="Carol")
        ab = Relationship(a, "KNOWS", b)
        bc = Relationship(b, "KNOWS", c)
        s = ab | bc
        assert s.order() == 3
        assert s.size() == 2
        assert set(s.nodes()) == {a, b, c}
        assert set(s.relationships()) == {ab, bc}

    def test_should_be_able_to_create_more_complex_union_using_operator(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        c = Node(name="Carol")
        d = Node(name="Dave")
        ab = Relationship(a, "KNOWS", b)
        bc = Relationship(b, "KNOWS", c)
        s = ab | bc | c | d
        assert s.order() == 4
        assert s.size() == 2
        assert set(s.nodes()) == {a, b, c, d}
        assert set(s.relationships()) == {ab, bc}


class NodeTestCase(TestCase):

    def test_should_be_able_to_create_empty_node(self):
        a = Node()
        assert a.labels() == set()
        assert dict(a) == {}

    def test_should_be_able_to_create_node_with_labels(self):
        a = Node("Person", "Employee")
        assert a.labels() == {"Person", "Employee"}
        assert dict(a) == {}

    def test_should_be_able_to_create_node_with_properties(self):
        a = Node(name="Alice", age=33)
        assert a.labels() == set()
        assert dict(a) == {"name": "Alice", "age": 33}

    def test_should_be_able_to_create_node_with_labels_and_properties(self):
        a = Node("Person", "Employee", name="Alice", age=33)
        assert a.labels() == {"Person", "Employee"}
        assert dict(a) == {"name": "Alice", "age": 33}

    def test_label_containment(self):
        a = Node("Person", name="Alice")
        assert "Person" in a.labels()

    def test_label_non_containment(self):
        a = Node("Person", name="Alice")
        assert "Employee" not in a.labels()

    def test_should_be_able_to_get_properties(self):
        a = Node("Person", name="Alice")
        assert a["name"] == "Alice"

    def test_missing_properties_should_default_to_none(self):
        a = Node("Person", name="Alice")
        assert a["age"] is None

    def test_should_not_be_able_to_set_properties(self):
        a = Node("Person", name="Alice")
        with self.assertRaises(TypeError):
            a["name"] = "Alfred"

    def test_should_be_able_to_get_property_keys(self):
        a = Node("Person", "Employee", name="Alice", age=33)
        assert set(a.keys()) == {"name", "age"}

    def test_should_be_able_to_get_property_values(self):
        a = Node("Person", "Employee", name="Alice", age=33)
        assert set(a.values()) == {"Alice", 33}

    def test_should_be_able_to_get_property_items(self):
        a = Node("Person", "Employee", name="Alice", age=33)
        assert set(a.items()) == {("name", "Alice"), ("age", 33)}

    def test_should_be_able_to_cast_to_dict(self):
        a = Node("Person", "Employee", name="Alice", age=33)
        assert dict(a) == {"name": "Alice", "age": 33}


class RelationshipTestCase(TestCase):

    a = Node("Person", name="Alice")
    b = Node("Person", name="Bob")

    def test_should_be_able_to_create_simple_relationship(self):
        ab = Relationship(self.a, "KNOWS", self.b, since=1999)
        assert ab.order() == 2
        assert ab.size() == 1
        assert ab.nodes() == (self.a, self.b)
        assert ab.type() == "KNOWS"
        assert dict(ab) == {"since": 1999}
