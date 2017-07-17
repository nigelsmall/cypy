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
Low-level graph data storage classes.
"""

from collections import namedtuple, Sequence, Set
from functools import reduce
from operator import and_ as and_operator
from threading import RLock
from uuid import UUID, uuid4

from cypy.collections import ReactiveSet, iter_items
from cypy.compat import atomic_types
from cypy.graph.abc import GraphStructure
from cypy.data import Value, Record


NodeEntry = namedtuple("NodeEntry", ["labels", "properties"])
RelationshipEntry = namedtuple("RelationshipEntry", ["type", "nodes", "properties"])


class PropertyValue(Value):
    """
    None - No
    Boolean - OK
    Integer - Within range
    Float - OK
    Bytes - Decode from Latin-1
    Unicode - OK
    List - Homogenous list of Boolean, Integer, Float or String
    Map - No
    Graph Structure - No
    """

    nullable = False

    @classmethod
    def coerce_list(cls, value):
        list_value = []
        item_type = None
        for item in value:
            item = cls.coerce(item)
            if not isinstance(item, atomic_types):
                raise ValueError("List properties can only contain simple atomic values "
                                 "that map to Java primitives and Strings")
            if item_type is None:
                item_type = type(item)
            elif type(item) != item_type:
                raise ValueError("List properties must be homogenous")
            list_value.append(item)
        return list_value

    @classmethod
    def coerce_map(cls, value):
        raise TypeError("Maps are not supported as property values")


class PropertyRecord(Record):
    """ Immutable key-value property store.
    """

    value_class = PropertyValue

    def __new__(cls, iterable=()):
        return Record.__new__(cls, sorted((key, value) for key, value in iter_items(iterable) if value is not None))

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__,
                               ", ".join("{}={!r}".format(key, value) for key, value in self.items()))


class PropertyDict(dict):
    """ Mutable key-value property store.

    A dictionary for property values that treats :const:`None`
    and missing values as semantically identical.

    PropertyDict instances can be created and used in a similar way
    to a standard dictionary. For example::

        >>> from cypy.graph.store import PropertyDict
        >>> fruit = PropertyDict({"name": "banana", "colour": "yellow"})
        >>> fruit["name"]
        'banana'

    The key difference with a PropertyDict is in how it handles
    missing values. Instead of raising a :py:class:`KeyError`,
    attempts to access a missing value will simply return
    :py:const:`None` instead.

    These are the operations that the PropertyDict can support:

   .. describe:: len(d)

        Return the number of items in the PropertyDict `d`.

   .. describe:: d[key]

        Return the item of `d` with key `key`. Returns :py:const:`None`
        if key is not in the map.

    """

    value_class = Value

    def __init__(self, iterable=None, **kwargs):
        dict.__init__(self)
        self.update(iterable, **kwargs)

    def __eq__(self, other):
        return dict.__eq__(self, {key: value for key, value in other.items() if value is not None})

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, key):
        return dict.get(self, key)

    def __setitem__(self, key, value):
        if value is None:
            try:
                dict.__delitem__(self, key)
            except KeyError:
                pass
        else:
            dict.__setitem__(self, key, self.value_class.coerce(value))

    def setdefault(self, key, default=None):
        if key in self:
            value = self[key]
        elif default is None:
            value = None
        else:
            value = dict.setdefault(self, key, default)
        return value

    def update(self, iterable=None, **kwargs):
        for key, value in dict(iterable or {}, **kwargs).items():
            self[key] = value


class GraphStore(GraphStructure):
    """ Low-level container for graph data.

    Internally, this object consists of five stores: two primary and three secondary.
    """

    # (a:Person {name: 'Alice'})-[r:KNOWS {since: 1999}]->(b:Person {name: 'Bob')

    # Node detail indexed by key.
    # This is a primary store.
    #
    # _nodes = {
    #     <node_key>: (<labels>, <properties>),
    #     "a": ({"Person"}, {"name": "Alice"}),
    #     "b": ({"Person"}, {"name": "Bob"}),
    # }
    #
    _nodes = None

    # Relationship detail indexed by key.
    # This is a primary store.
    #
    # _relationships = {
    #     <relationship_key>: (<type>, <nodes>, <properties>),
    #     "r": ("KNOWS", ("a", "b"), {"since": 1999}),
    # }
    #
    _relationships = None

    # Nodes indexed by label.
    # This is a secondary store.
    #
    # _nodes_by_label = {
    #     <label>: {<node_key>, <node_key>, ...}
    #     "Person": {"a", "b"},
    # }
    #
    _nodes_by_label = None

    # Relationships indexed by type.
    # This is a secondary store.
    #
    # {
    #     <type>: {<relationship_key>, <relationship_key>, ...},
    #     "KNOWS": {"r"},
    # }
    #
    _relationships_by_type = None

    # Relationships indexed by node.
    # This is a secondary store.
    #
    # {
    #     <node_key>: {(<relationship_key>, <index>), (<relationship_key>, <index>), ...},
    #     "a": {("r", 0)},
    #     "b": {("r", -1)},
    # }
    #
    _relationships_by_node = None

    def __graph_store__(self):
        return self

    @classmethod
    def build(cls, nodes=None, relationships=None):
        return cls(GraphStore(nodes, relationships))

    @classmethod
    def new_node_id(cls):
        return uuid4()

    @classmethod
    def new_relationship_id(cls):
        return uuid4()

    def __init__(self,
                 nodes=None,
                 relationships=None,
                 nodes_by_label=None,
                 relationships_by_type=None,
                 relationships_by_node=None):
        self._nodes = nodes or {}
        self._relationships = relationships or {}
        if nodes_by_label is None:
            self._build_nodes_by_label()
        else:
            self._nodes_by_label = nodes_by_label
        if relationships_by_type is None:
            self._build_relationships_by_type()
        else:
            self._relationships_by_type = relationships_by_type
        if relationships_by_node is None:
            self._build_relationships_by_node()
        else:
            self._relationships_by_node = relationships_by_node

    def dump(self):
        n = [node_str(key, labels, properties) for key, (labels, properties) in self._nodes.items()]
        r = [relationship_str(key, type, n, properties) for key, (type, n, properties) in self._relationships.items()]
        return "{}\n{}".format("\n".join(n), "\n".join(r))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._nodes == other._nodes and self._relationships == other._relationships
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        value = 0
        for node in self._nodes:
            value ^= hash(node)
        for relationship in self._relationships:
            value ^= hash(relationship)
        return value

    def _build_nodes_by_label(self):
        data = {}
        for node, (labels, _) in self._nodes.items():
            for label in labels:
                data.setdefault(label, set()).add(node)
        self._nodes_by_label = data

    def _build_relationships_by_type(self):
        data = {}
        for r_id, (r_type, _, _) in self._relationships.items():
            data.setdefault(r_type, set()).add(r_id)
        self._relationships_by_type = data

    def _build_relationships_by_node(self):
        data = {}
        for r_id, (_, n_ids, _) in self._relationships.items():
            for n_index, n_id in enumerate_nodes(n_ids):
                data.setdefault(n_id, set()).add((r_id, n_index))
        self._relationships_by_node = data

    def node_count(self, *n_labels):
        """ Count and return the number of nodes in this store.

        :param n_labels: count only nodes with all these labels
        :return: number of nodes
        """
        if not n_labels:
            return len(self._nodes)
        elif len(n_labels) == 1:
            return len(self._nodes_by_label.get(n_labels[0], ()))
        else:
            return sum(1 for _ in self.nodes(*n_labels))

    def nodes(self, *n_labels):
        """ Return an iterator over the node keys in this store,
        optionally filtered by label.
        """
        if n_labels:
            n_ids = ()
            n_id_sets = []
            for n_label in set(n_labels):
                try:
                    n_id_sets.append(self._nodes_by_label[n_label])
                except KeyError:
                    break
            else:
                n_ids = reduce(and_operator, n_id_sets)
        else:
            n_ids = self._nodes.keys()
        for n_id in n_ids:
            yield n_id

    def node_labels(self, n_id=None):
        """ Return the set of labels in this store or those for a specific node.
        """
        if n_id is None:
            return frozenset(self._nodes_by_label.keys())
        else:
            try:
                node_entry = self._nodes[n_id]
            except KeyError:
                return None
            else:
                return node_entry.labels

    def node_properties(self, n_id):
        try:
            node_entry = self._nodes[n_id]
        except KeyError:
            return None
        else:
            return node_entry.properties

    def relationship_count(self, r_type=None, n_ids=()):
        """ Count relationships filtered by type and endpoint.
        """
        if r_type is None and not n_ids:
            return len(self._relationships)
        elif not n_ids:
            return len(self._relationships_by_type.get(r_type, ()))
        else:
            return sum(1 for _ in self.relationships(r_type, n_ids))

    def relationships(self, r_type=None, n_ids=()):
        """ Match relationships filtered by type and endpoint.

        :param r_type:
        :param n_ids:
        :return:
        """
        if r_type is None:
            r_sets = []
        else:
            r_sets = [self._relationships_by_type.get(r_type, frozenset())]
        if not n_ids or (hasattr(n_ids, "__iter__") and all(n_id is None for n_id in n_ids)):
            pass
        elif isinstance(n_ids, Sequence):
            for n_index, n_id in enumerate_nodes(n_ids):
                if n_id is not None:
                    r_sets.append({r_id for r_id, i in self._relationships_by_node.get(n_id, ())
                                   if i == n_index})
        elif isinstance(n_ids, Set):
            for n_id in n_ids:
                if n_id is not None:
                    r_sets.append({r_id for r_id, i in self._relationships_by_node.get(n_id, ())})
        else:
            raise TypeError("Nodes must be supplied as a Sequence or a Set")
        if r_sets:
            return iter(reduce(and_operator, r_sets))
        else:
            return iter(self._relationships)

    def relationship_nodes(self, r_id):
        try:
            relationship_entry = self._relationships[r_id]
        except KeyError:
            return None
        else:
            return relationship_entry.nodes

    def relationship_properties(self, r_id):
        try:
            relationship_entry = self._relationships[r_id]
        except KeyError:
            return None
        else:
            return relationship_entry.properties

    def relationship_type(self, r_id):
        try:
            relationship_entry = self._relationships[r_id]
        except KeyError:
            return None
        else:
            return relationship_entry.type

    def relationship_types(self):
        """ Return the set of relationship types in this store.
        """
        return frozenset(self._relationships_by_type.keys())


class FrozenGraphStore(GraphStore):

    @classmethod
    def node_entry(cls, entry):
        labels, properties = entry
        return NodeEntry(frozenset(labels), PropertyRecord(properties))

    @classmethod
    def relationship_entry(cls, entry):
        type_, nodes, properties = entry
        return RelationshipEntry(type_, tuple(nodes), PropertyRecord(properties))

    def __init__(self, graph_store=None):
        if graph_store is None:
            super(FrozenGraphStore, self).__init__()
        elif isinstance(graph_store, FrozenGraphStore):
            super(FrozenGraphStore, self).__init__(nodes=graph_store._nodes,
                                                   relationships=graph_store._relationships,
                                                   nodes_by_label=graph_store._nodes_by_label,
                                                   relationships_by_type=graph_store._relationships_by_type,
                                                   relationships_by_node=graph_store._relationships_by_node)
        elif isinstance(graph_store, GraphStore):
            super(FrozenGraphStore, self).__init__()
            self._nodes.update((key, self.node_entry(entry))
                               for key, entry in graph_store._nodes.items())
            self._nodes_by_label.update((label, frozenset(nodes))
                                        for label, nodes in graph_store._nodes_by_label.items())
            self._relationships.update((key, self.relationship_entry(entry))
                                       for key, entry in graph_store._relationships.items())
            self._relationships_by_type.update((type_, frozenset(relationships))
                                               for type_, relationships in graph_store._relationships_by_type.items())
            self._relationships_by_node.update((node, frozenset(relationships))
                                               for node, relationships in graph_store._relationships_by_node.items())
        else:
            raise TypeError("Argument is not a graph store")


class MutableGraphStore(GraphStore):

    def node_entry(self, key, entry):

        def add_labels(*labels_):
            for label in labels_:
                self._nodes_by_label.setdefault(label, set()).add(key)

        def remove_labels(*labels_):
            for label in labels_:
                try:
                    self._nodes_by_label[label].discard(key)
                except KeyError:
                    pass

        labels, properties = entry
        return NodeEntry(ReactiveSet(labels, on_add=add_labels, on_remove=remove_labels), PropertyDict(properties))

    @classmethod
    def relationship_entry(cls, entry):
        type_, nodes, properties = entry
        return RelationshipEntry(type_, tuple(nodes), PropertyDict(properties))

    def __init__(self, graph_store=None):
        super(MutableGraphStore, self).__init__()
        self._lock = RLock()
        if graph_store is not None:
            self.update(graph_store)

    def _update_nodes(self, nodes):
        self._nodes.update((key, self.node_entry(key, entry)) for key, entry in nodes.items())

    def _update_relationships(self, relationships):
        self._relationships.update((key, self.relationship_entry(entry)) for key, entry in relationships.items())

    def _update_nodes_by_label(self, labels):
        for label, nodes in labels.items():
            self._nodes_by_label.setdefault(label, set()).update(nodes)

    def _update_relationships_by_type(self, relationships_by_type):
        for type_, relationships in relationships_by_type.items():
            self._relationships_by_type.setdefault(type_, set()).update(relationships)

    def _update_relationships_by_node(self, relationships_by_node):
        for n_id, entry in relationships_by_node.items():
            self._relationships_by_node.setdefault(n_id, set()).update(entry)

    def update(self, graph_store):
        if isinstance(graph_store, GraphStore):
            with self._lock:
                self._update_nodes(graph_store._nodes)
                self._update_relationships(graph_store._relationships)
                self._update_nodes_by_label(graph_store._nodes_by_label)
                self._update_relationships_by_type(graph_store._relationships_by_type)
                self._update_relationships_by_node(graph_store._relationships_by_node)
        else:
            raise TypeError("Argument is not a graph store")

    def add_nodes(self, entries):
        n_ids = []
        nodes = {}
        nodes_by_label = {}
        for entry in entries:
            n_id = self.new_node_id()
            mutable_entry = self.node_entry(n_id, entry)
            nodes[n_id] = mutable_entry
            for label in mutable_entry.labels:
                nodes_by_label.setdefault(label, set()).add(n_id)
            n_ids.append(n_id)
        with self._lock:
            self._update_nodes(nodes)
            self._update_nodes_by_label(nodes_by_label)
        return n_ids

    def remove_nodes(self, n_ids):
        with self._lock:
            for n_id in list(n_ids):
                # Remove from _nodes
                try:
                    n_labels, n_properties = self._nodes[n_id]
                except KeyError:
                    continue
                else:
                    del self._nodes[n_id]
                # Remove from _nodes_by_label
                for n_label in n_labels:
                    discard_value(self._nodes_by_label, n_label, n_id)
                # Remove relationships
                try:
                    self.remove_relationships(r_id for r_id, _ in self._relationships_by_node[n_id])
                except KeyError:
                    pass

    def add_relationships(self, entries):
        r_ids = []
        with self._lock:
            for r_type, n_ids, r_properties in entries:
                r_id = self.new_relationship_id()
                mutable_entry = self.relationship_entry((r_type, n_ids, r_properties))
                self._relationships[r_id] = mutable_entry
                self._relationships_by_type.setdefault(r_type, set()).add(r_id)
                for n_index, n_id in enumerate_nodes(n_ids):
                    self._relationships_by_node.setdefault(n_id, set()).add((r_id, n_index))
                r_ids.append(r_id)
        return r_ids

    def remove_relationships(self, r_ids):
        with self._lock:
            for r_id in list(r_ids):
                # Remove from _relationships
                try:
                    r_type, n_ids, r_properties = self._relationships[r_id]
                except KeyError:
                    continue
                else:
                    del self._relationships[r_id]
                # Remove from _relationships_by_type
                discard_value(self._relationships_by_type, r_type, r_id)
                # Remove from _relationships_by_node
                for n_index, n_id in enumerate_nodes(n_ids):
                    discard_value(self._relationships_by_node, n_id, (r_id, n_index))


def enumerate_nodes(iterable):
    try:
        size = len(iterable)
    except TypeError:
        iterable = list(iterable)
        size = len(iterable)
    last = size - 1
    for i, item in enumerate(iterable):
        yield -1 if i == last else i, item


def discard_value(collection, key, value):
    """ Discard an element from a value set.

    For a `collection` that maps `key` to {`value1`, `value2`, ...}, discard
    a specific `value` from the value set and drop the entire entry if the
    set becomes empty.
    """
    try:
        values = collection[key]
    except KeyError:
        pass
    else:
        values.discard(value)
        if not values:
            del collection[key]


def key_str(key):
    if isinstance(key, UUID):
        return "#" + key.hex[-7:]
    else:
        return key


def node_str(key, labels, properties):
    if labels:
        return "({}:{} {!r})".format(key_str(key), ":".join(labels), dict(properties))
    else:
        return "({} {!r})".format(key_str(key), dict(properties))


def relationship_str(key, type, node_keys, properties):
    return "({})-[{}:{} {!r}]->({})".format(key_str(node_keys[0]), key_str(key), type, dict(properties), ";".join(key_str(node_keys[1:])))