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


from collections import Sequence, Set
from itertools import chain

from cypy.data.abc import GraphStructure, GraphNode, GraphRelationship, GraphPath
from cypy.data.store import MutableGraphStore, FrozenGraphStore


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

    def __graph_order__(self):
        return self._store.node_count()

    def __graph_size__(self):
        return self._store.relationship_count()

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

    def _node(self, uuid):
        store = self._store
        node = Node(*store.node_labels(uuid), **store.node_properties(uuid))
        node.uuid = uuid
        return node

    @property
    def nodes(self):
        """ The set of nodes in this subgraph.
        """
        return frozenset(self._node(uuid) for uuid in self._store.nodes())

    @property
    def relationships(self):
        """ The set of relationships in this subgraph.
        """
        r_set = set()
        for uuid in self._store.relationships():
            relationship = Relationship(self._store.relationship_type(uuid),
                                        *map(self._node, self._store.relationship_nodes(uuid)),
                                        **self._store.relationship_properties(uuid))
            relationship.uuid = uuid
            r_set.add(relationship)
        return frozenset(r_set)


class Node(GraphNode):
    """ Immutable node object.
    """

    def __graph_store__(self):
        return self._store

    def __graph_order__(self):
        return 1

    def __graph_size__(self):
        return 0

    def __init__(self, *labels, **properties):
        self._uuid = FrozenGraphStore.new_node_key()
        self._store = FrozenGraphStore.build({self._uuid: (labels, properties)})

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ", ".join(
            chain(map(repr, self.labels), ("{}={!r}".format(*item) for item in dict(self).items()))))

    def __str__(self):
        if self.labels():
            return "(:{} {!r})".format(":".join(self.labels), dict(self))
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
            return set(self.labels) == set(other.labels) and dict(self) == dict(other)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._uuid)

    @property
    def uuid(self):
        """ Unique identifier for this node.
        """
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        store = self._store
        old_value = self._uuid
        store._nodes[value] = store._nodes[old_value]
        self._uuid = value
        del store._nodes[old_value]
        store._build_nodes_by_label()

    @property
    def labels(self):
        """ The set of labels attached to this node.
        """
        return self._store.node_labels(self._uuid)

    def keys(self):
        """ Return the property keys for this node.
        """
        return self._store.node_properties(self._uuid).keys()

    def values(self):
        """ Return the property values for this node.
        """
        return self._store.node_properties(self._uuid).values()

    def items(self):
        """ Return the full set of properties for this node.
        """
        return self._store.node_properties(self._uuid).items()


class Relationship(GraphRelationship):
    """ Immutable relationship object.
    """

    def __graph_store__(self):
        return self._store

    def __graph_order__(self):
        return len(set(self._nodes))

    def __graph_size__(self):
        return 1

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
            chain([repr(self.type)], map(repr, self.nodes), ("{}={!r}".format(*item) for item in dict(self).items()))))

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
            return (self.type == other.type and dict(self) == dict(other) and
                    tuple(node.uuid for node in self.nodes) == tuple(node.uuid for node in other.nodes))
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._uuid)

    @property
    def uuid(self):
        """ Unique identifier for this node.
        """
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

    @property
    def type(self):
        """ The type of this relationship.
        """
        from cypy.casing import relationship_case
        return self._store.relationship_type(self._uuid) or relationship_case(self.__class__.__name__)

    @property
    def nodes(self):
        """ The nodes connected by this relationship.
        """
        return self._nodes

    def keys(self):
        """ Return the property keys for this relationship.
        """
        return self._store.relationship_properties(self._uuid).keys()

    def values(self):
        """ Return the property values for this relationship.
        """
        return self._store.relationship_properties(self._uuid).values()

    def items(self):
        """ Return the full set of properties for this relationship.
        """
        return self._store.relationship_properties(self._uuid).items()


class Path(GraphPath):
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
            return [entity.nodes[0], entity] + list(entity.nodes[1:])
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
        self._store = Subgraph.union(*entities).__graph_store__()

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ", ".join(
            chain((repr(self._nodes[0]),), map(repr, self._relationships))))

    def __len__(self):
        return len(self._relationships)

    @property
    def nodes(self):
        """ The nodes in this path.
        """
        return tuple(self._nodes)

    @property
    def relationships(self):
        """ The relationships in this path.
        """
        return tuple(self._relationships)


class Graph(GraphStructure):
    """ Mutable graph data structure.
    """

    def __graph_store__(self):
        return self._store

    def __graph_order__(self):
        return self._store.node_count()

    def __graph_size__(self):
        return self._store.relationship_count()

    def __init__(self):
        self._store = MutableGraphStore()

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

    def __graph_order__(self):
        return 1

    def __graph_size__(self):
        return 0

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

    def __graph_order__(self):
        return len(self.nodes)

    def __graph_size__(self):
        return 1

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


def order(graph_structure):
    return graph_structure.__graph_order__()


def size(graph_structure):
    return graph_structure.__graph_size__()
