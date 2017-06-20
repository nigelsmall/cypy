====
CyPy
====

**CyPy** is a `Cypher <https://neo4j.com/developer/cypher/>`_ resource library for Python.
It provides facilities for client-side graph data storage as well as tools for working with the Cypher language.
The library uses consistent terminology with `Neo4j <https://neo4j.com/>`_ (*nodes*, *relationships*, *labels*, *properties* and so on) and provides a convenient local model for remote Neo4j interactions.
Several sets of classes are provided, these are described below.


``cypy.graph``
==============
In-memory graph data store.

Graph
-----
General purpose mutable graph data type

NodeView
--------
Accessor for a *node* in a `Graph`_

RelationshipView
----------------
Accessor for a *relationship* in a `Graph`_.


``cypy.subgraph``
=================
Classes for modelling immutable segments of graph data.

Node
----
TODO

Relationship
------------
TODO

Subgraph
--------
TODO


``cypy.store``
==============
Low-level graph data storage classes.

GraphStructure
--------------
TODO

GraphStore
----------
TODO

FrozenGraphStore
----------------
TODO

MutableGraphStore
-----------------
TODO


``cypy.values``
===============
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
