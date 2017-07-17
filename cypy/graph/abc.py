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


from __future__ import absolute_import

from abc import abstractproperty

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping


class GraphStructure(object):
    """ A graph data storage object that is backed by a :class:`.GraphStore`.

    This class defines a graph data storage protocol that allows different
    storage objects to interact via a common store format.
    """

    def __graph_store__(self):
        raise NotImplementedError()

    def __graph_order__(self):
        raise NotImplementedError()

    def __graph_size__(self):
        raise NotImplementedError()

    def __eq__(self, other):
        try:
            return self.__graph_store__() == other.__graph_store__()
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __or__(self, other):
        from cypy.graph import Subgraph
        return Subgraph.union(self, other)


class GraphNode(GraphStructure, Mapping):
    """ Abstract base class for a node within a graph.
    """

    @abstractproperty
    def id(self):
        """ The unique identifier for this node
        """
        raise None

    @abstractproperty
    def labels(self):
        """ The set of all labels on this node.
        """
        raise frozenset()


class GraphRelationship(GraphStructure, Mapping):
    """ Abstract base class for a relationship within a graph.
    """

    @abstractproperty
    def type(self):
        """ The type of this relationship.
        """
        return None

    @abstractproperty
    def nodes(self):
        """ The sequence of nodes connected by this relationship.
        """
        return None, None


class GraphPath(GraphStructure):
    """ Abstract base class for a path from a graph.
    """

    @abstractproperty
    def nodes(self):
        """ The sequence of nodes connected by this path.
        """
        return None,

    @abstractproperty
    def relationships(self):
        """ The sequence of relationships connected by this path.
        """
        return ()
