===================================================
``cypy.data`` -- Cypher data type and value support
===================================================

.. module:: cypy.data

.. autoclass:: cypy.data.Value
    :members:

.. class:: cypy.data.Record(iterable)

    A :class:`.Record` is an immutable ordered collection of key-value
    pairs. It is generally closer to a :py:class:`namedtuple` than to a
    :py:class:`OrderedDict` inasmuch as iteration of the collection will
    yield values rather than keys.

    A record can be constructed from any dict-like iterable. As with the
    built-in `dict` constructor, a `keys` method will be used if available,
    otherwise a sequence of key-value pairs will be assumed.

    The following two expressions produce similar records::

        >>> from cypy.data import Record
        >>> Record([("name", "Alice"), ("age", 33)])
        ('Alice', 33)
        >>> Record({"name": "Alice", "age": 33})
        ('Alice', 33)


    .. describe:: len(record)

        Return the number of fields in *record*.

    .. describe:: iter(record)

        Iterate through all values in *record*.

    .. describe:: dict(record)

        Return a :py:class:`dict` representation of *record*.

    .. describe:: record[index]

        Return the value of *record* at *index*.

    .. describe:: record[slice]

        Return a sub-record described by a *slice*.

    .. describe:: record[key]

        Return the value of *record* named by *key*.

    .. method:: get(key, default=None)

        Return the value of *record* named by *key* or *default* if the key does not exist.

    .. method:: index(key)

        Return the index of the field identified by `key`, raising a :py:class:`KeyError` if `key` is not found.

    .. method:: keys()

        Return a :py:class:`tuple` of keys.

    .. method:: values()

        Return a :py:class:`tuple` of values.

    .. method:: items()

        Return a :py:class:`tuple` of key-value pairs.
