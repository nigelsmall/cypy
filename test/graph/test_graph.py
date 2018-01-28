#!/usr/bin/env python
# coding: utf-8

# Copyright 2011-2018, Nigel Small
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

from cypy.graph import Subgraph, Node, Relationship, Graph, order, size


class GraphTestCase(TestCase):

    def test_should_be_able_to_create_empty_graph(self):
        g = Graph()
        dumped = Subgraph(g)
        assert order(dumped) == 0
        assert size(dumped) == 0
        assert set(dumped.nodes) == set()
        assert set(dumped.relationships) == set()

    def test_should_be_able_to_add_node_to_graph(self):
        a = Node(name="Alice")
        g = Graph()
        g.load(a)
        dumped = Subgraph(g)
        assert order(dumped) == 1
        assert size(dumped) == 0
        assert set(dumped.nodes) == {a}
        assert set(dumped.relationships) == set()

    def test_should_be_able_to_add_multiple_nodes_to_graph(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        g = Graph()
        g.load(a)
        g.load(b)
        dumped = Subgraph(g)
        assert order(dumped) == 2
        assert size(dumped) == 0
        assert set(dumped.nodes) == {a, b}
        assert set(dumped.relationships) == set()

    def test_should_be_able_to_add_subgraph_to_graph(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        g = Graph()
        g.load(Subgraph.union(a, b))
        dumped = Subgraph(g)
        assert order(dumped) == 2
        assert size(dumped) == 0
        assert set(dumped.nodes) == {a, b}
        assert set(dumped.relationships) == set()

    def test_should_be_able_to_add_relationships_to_graph(self):
        a = Node(name="Alice")
        b = Node(name="Bob")
        c = Node(name="Carol")
        ab = Relationship(a, "KNOWS", b)
        bc = Relationship(b, "KNOWS", c)
        g = Graph()
        g.load(Subgraph.union(ab, bc))
        dumped = Subgraph(g)
        assert order(dumped) == 3
        assert size(dumped) == 2
        assert set(dumped.nodes) == {a, b, c}
        assert set(dumped.relationships) == {ab, bc}

    def test_node_selection(self):
        g = Graph()
        a = g.create(name="Alice")
        b = g.create("X", name="Bob")
        c = g.create("Y", name="Carol")
        d = g.create("X", "Y", name="Dave")
        assert set(g.nodes()) == {a, b, c, d}
        assert set(g.nodes("X")) == {b, d}
        assert set(g.nodes("Y")) == {c, d}
        assert not set(g.nodes("Z"))
        assert set(g.nodes("X", "Y")) == {d}
        assert not set(g.nodes("X", "Z"))
        assert not set(g.nodes("Y", "Z"))
        assert not set(g.nodes("X", "Y", "Z"))

    def test_node_selection_deletion(self):
        g = Graph()
        a = g.create(name="Alice")
        b = g.create("X", name="Bob")
        c = g.create("Y", name="Carol")
        d = g.create("X", "Y", name="Dave")
        assert set(g.nodes()) == {a, b, c, d}
        g.nodes("Y").delete()
        assert set(g.nodes()) == {a, b}

    def test_main(self):
        n = [97]

        def new_node_key():
            key = chr(n[0])
            n[0] += 1
            return key

        graph = Graph()
        graph.__graph_store__().new_node_id = new_node_key
        a = graph.create("Person", "Employee", name="Alice", age=33)
        b = graph.create("Person", name="Bob", age=44)
        c = graph.create("Person", "Employee", name="Carol", age=55)
        d = graph.create("Person", "SelfEmployed", name="Dave", age=66)
        e = graph.create("Person", name="Eve", age=77)
        a.relate("KNOWS", b)
        a.relate("KNOWS", b, c)
        b.relate("KNOWS", a)
        a.relate("KNOWS", c)
        c.relate("KNOWS", a)
        a.relate("LIKES", c)
        c.relate("DISLIKES", b)
        c.relate("LOVES", d)
        d.relate("LOVES", c)
        d.relate("WORKS_FOR", d)
        print(graph._store.dump())


class GraphCreateTestCase(TestCase):

    def test_can_create_empty_nodes(self):
        g = Graph()
        g.create()
        assert order(g) == 1
        assert size(g) == 0
