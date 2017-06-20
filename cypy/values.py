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
Atomic values and collections.
"""


from functools import reduce
from operator import xor as xor_operator

from cypy.compat import integer, unicode


def iter_items(iterable):
    if hasattr(iterable, "keys"):
        for key in iterable.keys():
            yield key, iterable[key]
    else:
        for key, value in iterable:
            yield key, value


class Value(object):
    """
    None - OK
    Boolean - OK
    Integer - Within range
    Float - OK
    Bytes - Decode from Latin-1
    Unicode - OK
    List - OK
    Map - OK
    Graph Structure - OK
    """

    nullable = True
    default_encoding = "latin-1"

    @classmethod
    def coerce(cls, value):
        if value is None:
            return cls.coerce_null(value)
        elif isinstance(value, bool):
            return cls.coerce_boolean(value)
        elif isinstance(value, integer):
            return cls.coerce_integer(value)
        elif isinstance(value, float):
            return cls.coerce_float(value)
        elif isinstance(value, (unicode, bytes)):
            return cls.coerce_string(value)
        elif isinstance(value, list):
            return cls.coerce_list(value)
        elif isinstance(value, dict):
            return cls.coerce_map(value)
        else:
            raise TypeError("Values of type %s are not supported" % value.__class__.__name__)

    @classmethod
    def coerce_null(cls, _):
        if cls.nullable:
            return None
        else:
            raise ValueError("Null values are not supported")

    @classmethod
    def coerce_boolean(cls, value):
        return bool(value)

    @classmethod
    def coerce_integer(cls, value):
        if (-2 ** 63) <= value < (2 ** 63):
            return value
        else:
            raise ValueError("Integer value out of range: %s" % value)

    @classmethod
    def coerce_float(cls, value):
        return float(value)

    @classmethod
    def coerce_string(cls, value):
        if isinstance(value, unicode):
            return value
        else:
            return value.decode(cls.default_encoding)

    @classmethod
    def coerce_list(cls, value):
        return list(map(cls.coerce, value))

    @classmethod
    def coerce_map(cls, value):
        return {cls.coerce(key): cls.coerce(value) for key, value in value.items()}


class Record(tuple):

    value_class = Value

    __keys = None

    def __new__(cls, iterable):
        keys = []
        values = []
        for key, value in iter_items(iterable):
            keys.append(key)
            values.append(cls.value_class.coerce(value))
        inst = tuple.__new__(cls, values)
        inst.__keys = tuple(keys)
        return inst

    def __eq__(self, other):
        return dict(self) == dict(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, key):
        if isinstance(key, bytes):
            key = key.decode("latin-1")
        if isinstance(key, unicode):
            try:
                key = self.__keys.index(key)
            except ValueError:
                if self.value_class.nullable:
                    raise KeyError(key)
                else:
                    return None
        if 0 <= key < len(self) or self.value_class.nullable:
            return super(Record, self).__getitem__(key)
        else:
            return None

    def keys(self):
        return self.__keys

    def values(self):
        return tuple(self)

    def items(self):
        return tuple((self.__keys[i], super(Record, self).__getitem__(i)) for i in range(len(self)))


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
            if not isinstance(item, (bool, float, bytes, unicode)) and not isinstance(item, integer):
                raise ValueError("List properties can only contain primitive items")
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

    def __hash__(self):
        return reduce(xor_operator, map(hash, self.items()))


class PropertyDict(dict):
    """ Mutable key-value property store.

    A dictionary for property values that treats :const:`None`
    and missing values as semantically identical.

    PropertyDict instances can be created and used in a similar way
    to a standard dictionary. For example::

        >>> from py2neo import PropertyDict
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
