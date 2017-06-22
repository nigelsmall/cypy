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
In-memory graph data store.
"""

from collections import Sequence, Set
from itertools import chain

from cypy.data.abc import GraphStructure, GraphNode, GraphRelationship
from cypy.data.store import MutableGraphStore
from cypy.data.subgraph import Node, Subgraph


class Graph(GraphStructure):

    def __graph_store__(self):
        return self._store

    def __init__(self):
        self._store = MutableGraphStore()

    def order(self, *labels):
        return self._store.node_count(*labels)

    def size(self):
        return self._store.relationship_count()

    def dump(self):
        return Subgraph(self)

    def load(self, graph_structure):
        self._store.update(graph_structure.__graph_store__())

    def create(self, *labels, **properties):
        """ Create a node.

        :param labels:
        :param properties:
        :return:
        """
        node_key, = self._store.add_nodes([(labels, properties)])
        return NodeView(self._store, node_key)

    def nodes(self, *labels):
        """ Select one or more nodes by label.

        :param labels:
        :return: an iterable selection of nodes
        :rtype: :class:`.NodeSelection`
        """
        return NodeSelection(self._store, self._store.nodes(*labels))

    def relationships(self, type=None, nodes=()):
        """ Select one or more relationships by type and endpoints.
        """
        if isinstance(nodes, Sequence):
            return RelationshipSelection(self._store, self._store.relationships(type, [node.uuid for node in nodes]))
        elif isinstance(nodes, Set):
            return RelationshipSelection(self._store, self._store.relationships(type, {node.uuid for node in nodes}))
        else:
            raise TypeError("Nodes must be supplied as a Sequence or a Set")


class NodeSelection(object):
    """ A selection of nodes.
    """

    def __init__(self, store, selection):
        self._store = store
        self._selection = selection

    def __iter__(self):
        return self

    def __next__(self):
        return NodeView(self._store, next(self._selection))

    def next(self):
        return self.__next__()

    def delete(self):
        self._store.remove_nodes(self._selection)


class NodeView(GraphNode):
    """ Live view of a node in a graph.
    """

    def __graph_store__(self):
        raise NotImplementedError()

    def __init__(self, store, key):
        self._store = store
        self._uuid = key

    def __repr__(self):
        properties = self._store.node_properties(self._uuid)
        return "{}({})".format(self.__class__.__name__, ", ".join(
            chain(map(repr, self.labels()), ("{}={!r}".format(*item) for item in properties.items()))))

    def __str__(self):
        return "(#{}{} {!r})".format(self.uuid.hex[-7:], "".join(
            ":{}".format(label) for label in self.labels()), dict(self._store.node_properties(self._uuid)))

    def __getitem__(self, key):
        properties = self._store.node_properties(self._uuid)
        return properties[key]

    def __setitem__(self, key, value):
        properties = self._store.node_properties(self._uuid)
        properties[key] = value

    def __delitem__(self, key):
        properties = self._store.node_properties(self._uuid)
        del properties[key]

    def __len__(self):
        properties = self._store.node_properties(self._uuid)
        return len(properties)

    def __iter__(self):
        properties = self._store.node_properties(self._uuid)
        return iter(properties)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._store == other._store and self._uuid == other._uuid
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(id(self._store)) ^ hash(self._uuid)

    @property
    def uuid(self):
        return self._uuid

    def labels(self):
        return self._store.node_labels(self._uuid)

    def relationships(self, type, *nodes):
        """

        :param type:
        :param nodes:
        :return:
        """
        return self._store.relationships(type, n_keys=[node.uuid for node in nodes])

    def relate(self, *type_and_nodes, **properties):
        """ Relate this node to another.
        """
        if not type_and_nodes:
            raise TypeError("relate expected at least 1 argument, got 0")
        type_, nodes = type_and_nodes[0], list(type_and_nodes[1:])
        for i, node in enumerate(nodes):
            if isinstance(node, Node):
                node_key, = self._store.add_nodes([(node.labels(), node)])
                nodes[i] = node = NodeView(self._store, node_key)
            if not isinstance(node, NodeView):
                raise ValueError("Relationship endpoints must be Node or NodeView instances")
        key, = self._store.add_relationships([(type_, [node.uuid for node in [self] + nodes], properties)])
        return RelationshipView(self._store, key)

    def delete(self):
        pass


class RelationshipSelection(object):
    """ A selection of relationships.
    """

    def __init__(self, store, selection):
        self._store = store
        self._selection = selection

    def __iter__(self):
        return self

    def __next__(self):
        return RelationshipView(self._store, next(self._selection))

    def next(self):
        return self.__next__()

    def delete(self):
        self._store.remove_relationships(self._selection)


class RelationshipView(GraphRelationship):
    """ Live view of a relationship in a graph.
    """

    def __graph_store__(self):
        raise NotImplementedError()

    def __init__(self, store, uuid):
        self._store = store
        self._uuid = uuid

    def __getitem__(self, key):
        properties = self._store.relationship_properties(self._uuid)
        return properties[key]

    def __len__(self):
        properties = self._store.relationship_properties(self._uuid)
        return len(properties)

    def __iter__(self):
        properties = self._store.relationship_properties(self._uuid)
        return iter(properties)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._store == other._store and self._uuid == other._uuid
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(id(self._store)) ^ hash(self._uuid)

    # TODO: other methods

    @property
    def uuid(self):
        return self._uuid

    def type(self):
        from cypy.casing import relationship_case
        return self._store.relationship_type(self._uuid) or relationship_case(self.__class__.__name__)

    def nodes(self):
        """ Return the nodes connected by this relationship.
        """
        return tuple(self._store.relationship_nodes(self._uuid))
