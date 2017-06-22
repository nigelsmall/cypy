====
CyPy
====

.. image:: https://travis-ci.org/technige/cypy.svg?branch=master
    :target: https://travis-ci.org/technige/cypy

.. image:: https://coveralls.io/repos/github/technige/cypy/badge.svg?branch=master
    :target: https://coveralls.io/github/technige/cypy?branch=master


**CyPy** is a `Cypher <https://neo4j.com/developer/cypher/>`_ resource library for Python.
It provides facilities for client-side graph data storage as well as tools for working with the Cypher language.
The library uses terminology consistent with `Neo4j <https://neo4j.com/>`_ (*nodes*, *relationships*, *labels*, *properties*, etc) and provides a convenient local model for remote Neo4j interactions.


``cypy.data.abc``
=================
Abstract base classes for graph data types.

GraphStructure
--------------
TODO

GraphNode
---------
TODO

GraphRelationship
-----------------
TODO


``cypy.data.graph``
===================
In-memory graph data store.

Graph
-----
General purpose mutable graph data type

NodeSelection
-------------
TODO

NodeView
--------
Accessor for a *node* in a `Graph`_

RelationshipSelection
---------------------
TODO

RelationshipView
----------------
Accessor for a *relationship* in a `Graph`_.


``cypy.data.store``
===================
Low-level graph data storage classes.

GraphStore
----------
TODO

FrozenGraphStore
----------------
TODO

MutableGraphStore
-----------------
TODO


``cypy.data.subgraph``
======================
Classes for modelling immutable segments of graph data.

Subgraph
--------
TODO

Node
----
TODO

Relationship
------------
TODO


``cypy.data.values``
====================
Atomic values and collections.

Value
-----
TODO

Record
------
TODO

PropertyValue
-------------
TODO

PropertyRecord
--------------
TODO

PropertyDict
------------
TODO


``cypy.lang.casing``
====================
TODO

snake_case
----------
TODO

title_case
----------
TODO

relationship_case
-----------------
TODO

label_case
----------
TODO


``cypy.lang.encoding``
======================
TODO

CypherEncoder
-------------
TODO

LabelSetView
------------
TODO

PropertyDictView
----------------
TODO

PropertySelector
----------------
TODO

cypher_escape
-------------
TODO

cypher_repr
-----------
TODO

cypher_str
----------
TODO


``cypy.lang.lex``
=================
TODO

CypherLexer
-----------
TODO


``cypy.collections``
====================
TODO

ReactiveSet
-----------
TODO
