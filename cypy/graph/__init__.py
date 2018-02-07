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


"""
General purpose graph data storage classes for both mutable and immutable data.
"""


from collections import Sequence, Set
from itertools import chain
from re import compile as re_compile

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

from cypy.graph.store import GraphStructure, MutableGraphStore, FrozenGraphStore


class Node(GraphStructure, Mapping):
    """ Immutable node object.
    """

    def __graph_store__(self):
        return self._store

    def __graph_order__(self):
        return 1

    def __graph_size__(self):
        return 0

    @classmethod
    def compose(cls, id, labels, properties):
        inst = super(Node, cls).__new__(cls)
        inst._id = id
        inst._store = FrozenGraphStore.build({inst._id: (labels, properties)})
        return inst

    @classmethod
    def view(cls, store, n_key):
        inst = super(Node, cls).__new__(cls)
        inst._id = n_key
        inst._store = store
        return inst

    def __init__(self, *labels, **properties):
        self._id = FrozenGraphStore.new_node_id()
        self._store = FrozenGraphStore.build({self._id: (labels, properties)})

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ", ".join(
            chain(map(repr, self.labels()), ("{}={!r}".format(*item) for item in dict(self).items()))))

    def __str__(self):
        if self.labels():
            return "(:{} {!r})".format(":".join(self.labels()), dict(self))
        else:
            return "({!r})".format(dict(self))

    def __bool__(self):
        return bool(self._store.node_properties(self._id))

    def __nonzero__(self):
        return bool(self._store.node_properties(self._id))

    def __len__(self):
        return len(self._store.node_properties(self._id))

    def __iter__(self):
        return iter(self._store.node_properties(self._id))

    def __getitem__(self, key):
        return self._store.node_properties(self._id)[key]

    def __setitem__(self, key, value):
        properties = self._store.node_properties(self._id)
        try:
            properties[key] = value
        except TypeError:
            raise TypeError("Node does not support property assignment")

    def __delitem__(self, key):
        properties = self._store.node_properties(self._id)
        try:
            del properties[key]
        except TypeError:
            raise TypeError("Node does not support property deletion")

    def __eq__(self, other):
        try:
            return set(self.labels()) == set(other.labels()) and dict(self) == dict(other)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._id)

    @property
    def id(self):
        """ Unique identifier for this node.
        """
        return self._id

    def labels(self):
        """ Return the set of all labels on this node.

        :return: `frozenset` containing labels as strings
        """
        return self._store.node_labels(self._id)

    def keys(self):
        """ Return the property keys for this node.
        """
        return self._store.node_properties(self._id).keys()

    def values(self):
        """ Return the property values for this node.
        """
        return self._store.node_properties(self._id).values()

    def items(self):
        """ Return the full set of properties for this node.
        """
        return self._store.node_properties(self._id).items()


class Relationship(GraphStructure, Mapping):
    """ Immutable relationship object.
    """

    @classmethod
    def default_type(cls, relationship):
        word_first = re_compile(r"(.)([A-Z][a-z]+)")
        word_all = re_compile(r"([a-z0-9])([A-Z])")
        s1 = word_first.sub(r"\1_\2", relationship.__class__.__name__)
        return word_all.sub(r"\1_\2", s1).upper()

    def __graph_store__(self):
        return self._store

    def __graph_order__(self):
        return len(set(self._nodes))

    def __graph_size__(self):
        return 1

    @classmethod
    def compose(cls, id, properties, *nodes):
        node_keys = []
        node_dict = {}
        for node in nodes:
            store = node.__graph_store__()
            other_node_key = list(store.nodes())[0]
            node_labels = store.node_labels(other_node_key)
            node_properties = store.node_properties(other_node_key)
            node_key = node.id
            node_keys.append(node_key)
            node_dict[node_key] = (node_labels, node_properties)
        inst = super(Relationship, cls).__new__(cls)
        inst._id = id
        inst._store = FrozenGraphStore.build(node_dict, {inst._id: (cls, node_keys, properties)})
        inst._nodes = tuple(nodes)
        return inst

    @classmethod
    def view(cls, store, r_key):
        inst = super(Relationship, cls).__new__(cls)
        inst._id = r_key
        inst._store = store
        inst._nodes = tuple(Node.view(store, n_key) for n_key in store.relationship_nodes(r_key))
        return inst

    def __init__(self, *nodes, **properties):
        type_ = type(self)
        node_keys = []
        node_dict = {}
        for node in nodes:
            if not isinstance(node, Node):
                raise ValueError("Relationships can only connect nodes (%r passed)" % node)
            store = node.__graph_store__()
            other_node_key = list(store.nodes())[0]
            node_labels = store.node_labels(other_node_key)
            node_properties = store.node_properties(other_node_key)
            node_key = node.id
            node_keys.append(node_key)
            node_dict[node_key] = (node_labels, node_properties)
        self._id = FrozenGraphStore.new_relationship_id()
        self._store = FrozenGraphStore.build(node_dict, {self._id: (type_, node_keys, properties)})
        self._nodes = tuple(nodes)

    def __repr__(self):
        return "{}({})".format(type(self).__name__, ", ".join(
            chain(map(repr, self.nodes()), ("{}={!r}".format(*item) for item in dict(self).items()))))

    def __str__(self):
        if bool(self):
            return "()-[:{} {}]->()".format(type(self).__name__, dict(self))
        else:
            return "()-[:{}]->()".format(type(self).__name__)

    def __bool__(self):
        return bool(self._store.relationship_properties(self._id))

    def __nonzero__(self):
        return bool(self._store.relationship_properties(self._id))

    def __len__(self):
        return len(self._store.relationship_properties(self._id))

    def __iter__(self):
        return iter(self._store.relationship_properties(self._id))

    def __getitem__(self, key):
        return self._store.relationship_properties(self._id)[key]

    def __setitem__(self, key, value):
        properties = self._store.relationship_properties(self._id)
        try:
            properties[key] = value
        except TypeError:
            raise TypeError("Relationship does not support property assignment")

    def __delitem__(self, key):
        properties = self._store.relationship_properties(self._id)
        try:
            del properties[key]
        except TypeError:
            raise TypeError("Relationship does not support property deletion")

    def __eq__(self, other):
        try:
            return (type(self) == type(other) and dict(self) == dict(other) and
                    tuple(node.id for node in self.nodes()) == tuple(node.id for node in other.nodes()))
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._id)

    @property
    def id(self):
        """ Unique identifier for this node.
        """
        return self._id

    def nodes(self):
        """ The nodes connected by this relationship.
        """
        return self._nodes

    def keys(self):
        """ Return the property keys for this relationship.
        """
        return self._store.relationship_properties(self._id).keys()

    def values(self):
        """ Return the property values for this relationship.
        """
        return self._store.relationship_properties(self._id).values()

    def items(self):
        """ Return the full set of properties for this relationship.
        """
        return self._store.relationship_properties(self._id).items()


class Path(GraphStructure):
    """ A captured walk through a graph structure.
    """

    def __graph_store__(self):
        return self._store

    def __graph_order__(self):
        return len(self._nodes)

    def __graph_size__(self):
        return len(self._relationships)

    @classmethod
    def _append(cls, entities, *tail):
        for walkable in tail:
            next_entity = list(cls._walk(walkable))
            if entities[-1] == next_entity[0]:
                entities.extend(next_entity[1:])
            elif entities[-1] == next_entity[-1]:
                entities.extend(reversed(next_entity[:-1]))
            else:
                raise ValueError("Cannot concatenate {!r} to {!r}".format(next_entity, entities[-1]))

    @classmethod
    def _walk(cls, entity):
        if hasattr(entity, "nodes"):
            nodes = entity.nodes()
            return [nodes[0], entity] + list(nodes[1:])
        else:
            return [entity]

    def __init__(self, head, *tail):
        entities = self._walk(head)
        try:
            self._append(entities, *tail)
        except ValueError:
            entities = list(reversed(self._walk(head)))
            self._append(entities, *tail)
        self._nodes = entities[0::2]
        self._relationships = entities[1::2]
        self._store = self.union(*entities).__graph_store__()

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ", ".join(
            chain((repr(self._nodes[0]),), map(repr, self._relationships))))

    def __len__(self):
        return len(self._relationships)

    def nodes(self):
        """ The nodes in this path.
        """
        return tuple(self._nodes)

    def relationships(self):
        """ The relationships in this path.
        """
        return tuple(self._relationships)


class FrozenGraph(GraphStructure):
    """ Immutable graph data structure.
    """

    def __graph_store__(self):
        return self._store

    def __graph_order__(self):
        return self._store.node_count()

    def __graph_size__(self):
        return self._store.relationship_count()

    def __init__(self, graph_structure=None):
        if graph_structure is None:
            self._store = FrozenGraphStore()
        else:
            self._store = FrozenGraphStore(graph_structure.__graph_store__())

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

    def nodes(self, *labels):
        """ Select one or more nodes by label.

        :param labels:
        :return: an iterable selection of nodes
        :rtype: :class:`.NodeSelection`
        """
        return NodeSelection(self._store, self._store.nodes(*labels))

    def relationships(self, r_type=None, nodes=()):
        """ Select one or more relationships by type and endpoints.
        """
        if isinstance(nodes, Sequence):
            return RelationshipSelection(self._store, self._store.relationships(r_type, [node.id for node in nodes]))
        elif isinstance(nodes, Set):
            return RelationshipSelection(self._store, self._store.relationships(r_type, {node.id for node in nodes}))
        else:
            raise TypeError("Nodes must be supplied as a Sequence or a Set")


class Graph(GraphStructure):
    """ Mutable graph data structure.
    """

    def __graph_store__(self):
        return self._store

    def __graph_order__(self):
        return self._store.node_count()

    def __graph_size__(self):
        return self._store.relationship_count()

    def __init__(self, graph_structure=None):
        self._store = MutableGraphStore()
        if graph_structure is not None:
            self._store.update(graph_structure.__graph_store__())

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

    def update(self, graph_structure):
        self._store.update(graph_structure.__graph_store__())

    def create(self, *labels, **properties):
        """ Create a node.

        :param labels:
        :param properties:
        :return:
        """
        n_key, = self._store.add_nodes([(labels, properties)])
        return Node.view(self._store, n_key)

    def nodes(self, *labels):
        """ Select one or more nodes by label.

        :param labels:
        :return: an iterable selection of nodes
        :rtype: :class:`.NodeSelection`
        """
        return NodeSelection(self._store, self._store.nodes(*labels))

    def relationships(self, r_type=None, nodes=()):
        """ Select one or more relationships by type and endpoints.
        """
        if isinstance(nodes, Sequence):
            return RelationshipSelection(self._store, self._store.relationships(r_type, [node.id for node in nodes]))
        elif isinstance(nodes, Set):
            return RelationshipSelection(self._store, self._store.relationships(r_type, {node.id for node in nodes}))
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
        return Node.view(self._store, next(self._selection))

    def next(self):
        return self.__next__()

    def delete(self):
        self._store.remove_nodes(self._selection)


class RelationshipSelection(object):
    """ A selection of relationships.
    """

    def __init__(self, store, selection):
        self._store = store
        self._selection = selection

    def __iter__(self):
        return self

    def __next__(self):
        r_key = next(self._selection)
        r_type = self._store.relationship_type(r_key)
        return r_type.view(self._store, r_key)

    def next(self):
        return self.__next__()

    def delete(self):
        self._store.remove_relationships(self._selection)


def relationship_type(name, base_class=Relationship):
    if not issubclass(base_class, Relationship):
        raise TypeError("Base class must extend %s" % Relationship.__class__)
    if isinstance(name, str):
        str_name = name
    else:
        try:
            str_name = name.encode("utf-8")
        except AttributeError:
            raise ValueError("Invalid type name %r" % name)
    return type(str_name, (base_class,), {})


def order(graph_structure):
    """ Count the number of nodes in a graph structure.
    """
    try:
        return graph_structure.__graph_order__()
    except AttributeError:
        raise TypeError("Object is not a graph structure")


def size(graph_structure):
    """ Count the number of relationships in a graph structure.
    """
    try:
        return graph_structure.__graph_size__()
    except AttributeError:
        raise TypeError("Object is not a graph structure")


def _relationship_case(s):
    word_first = re_compile(r"(.)([A-Z][a-z]+)")
    word_all = re_compile(r"([a-z0-9])([A-Z])")
    s1 = word_first.sub(r"\1_\2", s)
    return word_all.sub(r"\1_\2", s1).upper()
