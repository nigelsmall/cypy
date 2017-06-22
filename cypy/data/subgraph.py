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
Classes for modelling immutable segments of graph data.
"""

from itertools import chain

from cypy.data.abc import GraphStructure, GraphNode, GraphRelationship
from cypy.data.store import FrozenGraphStore, MutableGraphStore


class Subgraph(GraphStructure):
    """ Immutable collection of nodes and relationships.
    """

    @classmethod
    def union(cls, *graph_structures):
        store = MutableGraphStore()
        for graph_structure in graph_structures:
            try:
                sub_store = graph_structure.__graph_store__()
            except AttributeError:
                raise TypeError("{} object is not a graph structure".format(type(graph_structure)))
            else:
                store.update(sub_store)
        return Subgraph(store)

    def __graph_store__(self):
        return self._store

    def __init__(self, graph_structure=None):
        if graph_structure is None:
            self._store = FrozenGraphStore()
        else:
            try:
                store = graph_structure.__graph_store__()
            except AttributeError:
                raise TypeError("{} object is not a graph structure".format(type(graph_structure)))
            else:
                self._store = FrozenGraphStore(store)

    def __repr__(self):
        # TODO: something better here
        return "Subgraph" + repr(self._store)

    def __bool__(self):
        return self._store.relationship_count() != 0

    def __nonzero__(self):
        return self._store.relationship_count() != 0

    def __len__(self):
        return self._store.relationship_count()

    def __eq__(self, other):
        try:
            return self.__graph_store__() == other.__graph_store__()
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__graph_store__())

    def order(self, *labels):
        return self._store.node_count(*labels)

    def size(self, type=None):
        return self._store.relationship_count(r_type=type)

    def _node(self, uuid):
        store = self._store
        node = Node(*store.node_labels(uuid), **store.node_properties(uuid))
        node.uuid = uuid
        return node

    def nodes(self, *labels):
        store = self._store
        for uuid in store.nodes(*labels):
            yield self._node(uuid)

    def relationships(self, type=None, nodes=()):
        store = self._store
        for uuid in store.relationships(r_type=type, n_keys=nodes):
            relationship = Relationship(store.relationship_type(uuid),
                                        *map(self._node, store.relationship_nodes(uuid)),
                                        **store.relationship_properties(uuid))
            relationship.uuid = uuid
            yield relationship


class Node(GraphNode):
    """ Immutable node object.
    """

    def __graph_store__(self):
        return self._store

    def __init__(self, *labels, **properties):
        self._uuid = FrozenGraphStore.new_node_key()
        self._store = FrozenGraphStore.build({self._uuid: (labels, properties)})

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ", ".join(
            chain(map(repr, self.labels()), ("{}={!r}".format(*item) for item in dict(self).items()))))

    def __str__(self):
        if self.labels():
            return "(:{} {!r})".format(":".join(self.labels()), dict(self))
        else:
            return "({!r})".format(dict(self))

    def __bool__(self):
        return bool(self._store.node_properties(self._uuid))

    def __nonzero__(self):
        return bool(self._store.node_properties(self._uuid))

    def __len__(self):
        return len(self._store.node_properties(self._uuid))

    def __iter__(self):
        return iter(self._store.node_properties(self._uuid))

    def __getitem__(self, key):
        return self._store.node_properties(self._uuid)[key]

    def __eq__(self, other):
        try:
            return self.labels() == other.labels() and dict(self) == dict(other)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._uuid)

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        store = self._store
        old_value = self._uuid
        store._nodes[value] = store._nodes[old_value]
        self._uuid = value
        del store._nodes[old_value]
        store._build_nodes_by_label()

    def order(self):
        return 1

    def size(self):
        return 0

    def labels(self):
        return self._store.node_labels(self._uuid)

    def keys(self):
        return self._store.node_properties(self._uuid).keys()

    def values(self):
        return self._store.node_properties(self._uuid).values()

    def items(self):
        return self._store.node_properties(self._uuid).items()


class Relationship(GraphRelationship):
    """ Immutable relationship object.
    """

    def __graph_store__(self):
        return self._store

    def __init__(self, *type_and_nodes, **properties):
        type_ = None
        node_keys = []
        nodes = []
        node_dict = {}
        for arg in type_and_nodes:
            if isinstance(arg, Node):
                store = arg.__graph_store__()
                other_node_key = list(store.nodes())[0]
                node_labels = store.node_labels(other_node_key)
                node_properties = store.node_properties(other_node_key)
                node_key = arg.uuid
                node_keys.append(node_key)
                nodes.append(arg)
                node_dict[node_key] = (node_labels, node_properties)
            elif type_ is None:
                type_ = arg
            else:
                raise ValueError("Relationships can only have one type and must connect nodes")
        self._uuid = FrozenGraphStore.new_relationship_key()
        self._store = FrozenGraphStore.build(node_dict, {self._uuid: (type_, node_keys, properties)})
        self._node_keys = node_keys
        self._nodes = tuple(nodes)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ", ".join(
            chain([repr(self.type())], map(repr, self.nodes()), ("{}={!r}".format(*item) for item in dict(self).items()))))

    def __str__(self):
        if bool(self):
            return "()-[:{} {}]->()".format(self.type(), dict(self))
        else:
            return "()-[:{}]->()".format(self.type())

    def __bool__(self):
        return bool(self._store.relationship_properties(self._uuid))

    def __nonzero__(self):
        return bool(self._store.relationship_properties(self._uuid))

    def __len__(self):
        return len(self._store.relationship_properties(self._uuid))

    def __iter__(self):
        return iter(self._store.relationship_properties(self._uuid))

    def __getitem__(self, key):
        return self._store.relationship_properties(self._uuid)[key]

    def __eq__(self, other):
        try:
            return (self.type() == other.type() and dict(self) == dict(other) and
                    tuple(node.uuid for node in self.nodes()) == tuple(node.uuid for node in other.nodes()))
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._uuid)

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        store = self._store
        old_value = self._uuid
        store._relationships[value] = store._relationships[old_value]
        self._uuid = value
        del store._relationships[old_value]
        store._build_relationships_by_node()
        store._build_relationships_by_type()

    def order(self):
        return len(self._nodes)

    def size(self):
        return 1

    def type(self):
        from cypy.casing import relationship_case
        return self._store.relationship_type(self._uuid) or relationship_case(self.__class__.__name__)

    def nodes(self):
        return self._nodes

    def start_node(self):
        try:
            return self._nodes[0]
        except IndexError:
            return None

    def end_node(self):
        try:
            return self._nodes[-1]
        except IndexError:
            return None

    def keys(self):
        return self._store.relationship_properties(self._uuid).keys()

    def values(self):
        return self._store.relationship_properties(self._uuid).values()

    def items(self):
        return self._store.relationship_properties(self._uuid).items()
