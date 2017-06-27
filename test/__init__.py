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


from cypy.data import Node, Relationship, Graph


def main():
    g = Graph()
    a = Node(name="Alice")
    b = Node(name="Bob")
    c = Node(name="Carol")
    d = Node(name="Dave")
    ab = Relationship(a, "KNOWS", b)
    ac = Relationship(a, "LIKES", c)
    cb = Relationship(c, "DISLIKES", b)
    cd = Relationship(c, "MARRIED_TO", d)
    dd = Relationship(d, "WORKS_FOR", d)
    g |= ab | ac | cb | cd | dd
    for node in g.nodes():
        print(node)
    for relationship in g.relationships():
        print(relationship)
