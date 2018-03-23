#!/usr/bin/env python
# coding: utf-8

# Copyright 2002-2018, Neo4j
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

from cypy.graph import Node, relationship_type, Graph, FrozenGraph, graph_order, graph_size


KNOWS = relationship_type("KNOWS")


class NodeTestCase(TestCase):

    def test_can_create_node_with_default_constructor(self):
        a = Node("Person", name="Alice")
        self.assertFalse(a.is_mutable())
        self.assertEqual(set(a.labels()), {"Person"})
        self.assertEqual(dict(a), {"name": "Alice"})

    def test_can_create_node_with_advanced_constructor(self):
        a = Node.build("a", ["Person"], {"name": "Alice"})
        self.assertFalse(a.is_mutable())
        self.assertEqual(a.id, "a")
        self.assertEqual(set(a.labels()), {"Person"})
        self.assertEqual(dict(a), {"name": "Alice"})

    def test_can_create_node_view(self):
        original = Node("Person", name="Alice")
        a = Node.view(original, original.id)
        self.assertEqual(a.is_mutable(), original.is_mutable())
        self.assertEqual(set(a.labels()), {"Person"})
        self.assertEqual(dict(a), {"name": "Alice"})

    def test_node_order(self):
        a = Node("Person", name="Alice")
        self.assertEqual(graph_order(a), 1)

    def test_node_size(self):
        a = Node("Person", name="Alice")
        self.assertEqual(graph_size(a), 0)

    def test_node_labels(self):
        a = Node("Person", "Employee", name="Alice")
        self.assertEqual(set(a.labels()), {"Person", "Employee"})

    def test_node_properties(self):
        a = Node("Person", name="Alice", age=33)
        self.assertEqual(set(a.keys()), {"name", "age"})
        self.assertEqual(set(a.values()), {"Alice", 33})
        self.assertEqual(set(a.items()), {("name", "Alice"), ("age", 33)})

    def test_node_property_assignment(self):
        g = Graph(Node("Person", name="Alice"))
        a = next(g.nodes())
        self.assertEqual(set(a.items()), {("name", "Alice")})
        a["age"] = 33
        self.assertEqual(set(a.items()), {("name", "Alice"), ("age", 33)})

    def test_node_property_deletion(self):
        g = Graph(Node("Person", name="Alice", age=33))
        a = next(g.nodes())
        self.assertEqual(set(a.items()), {("name", "Alice"), ("age", 33)})
        del a["age"]
        self.assertEqual(set(a.items()), {("name", "Alice")})

    def test_node_coercion_to_bool(self):
        a = Node(name="Alice")
        self.assertEqual(bool(a), True)
        self.assertEqual(a.__bool__(), True)
        self.assertEqual(a.__nonzero__(), True)
        z = Node()
        self.assertEqual(bool(z), False)
        self.assertEqual(z.__bool__(), False)
        self.assertEqual(z.__nonzero__(), False)

    def test_node_len(self):
        a = Node("Person", name="Alice", age=33)
        self.assertEqual(len(a), 2)

    def test_node_coercion_to_set(self):
        a = Node("Person", name="Alice", age=33)
        self.assertEqual(set(a), {"Alice", 33})

    def test_node_coercion_to_dict(self):
        a = Node("Person", name="Alice", age=33)
        self.assertEqual(dict(a), {"name": "Alice", "age": 33})

    def test_node_equality(self):
        a1 = Node("Person", name="Alice")
        a2 = Node("Person", name="Alice")
        self.assertEqual(a1, a2)

    def test_node_inequality(self):
        a = Node("Person", name="Alice")
        b = Node("Person", name="Bob")
        self.assertNotEqual(a, b)

    def test_static_labels(self):

        class Person(Node):
            __labels__ = ("Person",)

        a1 = Person(name="Alice")
        self.assertEqual(set(a1.labels()), {"Person"})

        a2 = Person("Employee", name="Alice")
        self.assertEqual(set(a2.labels()), {"Person", "Employee"})


class GraphTestCase(TestCase):

    def test_should_be_able_to_create_empty_graph(self):
        g = Graph()
        assert graph_order(g) == 0
        assert graph_size(g) == 0
        assert set(g.nodes()) == set()
        assert set(g.relationships()) == set()

    def test_should_be_able_to_add_node_to_graph(self):
        a = Node(name="Alice")
        g = Graph()
        g.update(a)
        f = FrozenGraph(g)
        assert graph_order(f) == 1
        assert graph_size(f) == 0
        assert set(f.nodes()) == {a}
        assert set(f.relationships()) == set()

    def test_should_be_able_to_add_multiple_nodes_to_graph(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        g = Graph()
        g.update(a)
        g.update(b)
        f = FrozenGraph(g)
        assert graph_order(f) == 2
        assert graph_size(f) == 0
        assert set(f.nodes()) == {a, b}
        assert set(f.relationships()) == set()

    def test_should_be_able_to_add_subgraph_to_graph(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        g = Graph(a | b)
        f = FrozenGraph(g)
        assert graph_order(f) == 2
        assert graph_size(f) == 0
        assert set(f.nodes()) == {a, b}
        assert set(f.relationships()) == set()

    def test_should_be_able_to_add_relationships_to_graph(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        c = Node(name="Carol")
        ab = KNOWS(a, b)
        bc = KNOWS(b, c)
        g = Graph(a | b | c | ab | bc)
        f = FrozenGraph(g)
        assert graph_order(f) == 3
        assert graph_size(f) == 2
        assert set(f.nodes()) == {a, b, c}
        assert set(f.relationships()) == {ab, bc}

    def test_node_selection(self):
        a = Node(name="Alice")
        b = Node("X", name="Bob")
        c = Node("Y", name="Carol")
        d = Node("X", "Y", name="Dave")
        g = Graph(a | b | c | d)
        assert set(g.nodes()) == {a, b, c, d}
        assert set(g.nodes("X")) == {b, d}
        assert set(g.nodes("Y")) == {c, d}
        assert not set(g.nodes("Z"))
        assert set(g.nodes("X", "Y")) == {d}
        assert not set(g.nodes("X", "Z"))
        assert not set(g.nodes("Y", "Z"))
        assert not set(g.nodes("X", "Y", "Z"))

    def test_node_selection_deletion(self):
        a = Node(name="Alice")
        b = Node("X", name="Bob")
        c = Node("Y", name="Carol")
        d = Node("X", "Y", name="Dave")
        g = Graph(a | b | c | d)
        self.assertEqual(set(g.nodes()), {a, b, c, d})
        g.nodes("Y").delete()
        self.assertEqual(set(g.nodes()), {a, b})

    def test_can_update_properties_on_entities_within_a_graph(self):
        alice = Node("Person", name="Alice")
        bob = Node("Person", name="Bob")
        g = Graph(alice | bob | KNOWS(alice, bob))
        nodes = set(g.nodes())
        self.assertEqual(len(nodes), 2)
        a = [node for node in nodes if node["name"] == "Alice"][0]
        b = [node for node in nodes if node["name"] == "Bob"][0]
        self.assertIn(a, nodes)
        self.assertIn(b, nodes)
        relationships = list(g.relationships())
        self.assertEqual(len(relationships), 1)
        self.assertEqual(b["name"], "Bob")
        b["name"] = "Robert"
        self.assertEqual(b["name"], "Robert")
        self.assertEqual(len(relationships), 1)
        ab = relationships[0]
        self.assertIsNone(ab["since"])
        ab["since"] = 1999
        self.assertEqual(ab["since"], 1999)


class GraphCreateTestCase(TestCase):

    def test_can_create_empty_nodes(self):
        g = Graph()
        g.create()
        assert graph_order(g) == 1
        assert graph_size(g) == 0
