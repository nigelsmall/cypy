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


from functools import reduce
from operator import xor as xor_operator

from cypy.compat import unicode, integer
from cypy.data.values import Value, Record, iter_items
from cypy.encoding import cypher_repr, cypher_str


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

        >>> from cypy.data.properties import PropertyDict
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


class PropertyDictView(object):

    def __init__(self, items=(), selected=(), **kwargs):
        self.__items = dict(items)
        self.__selected = tuple(selected)
        self.__kwargs = kwargs

    def __repr__(self):
        if self.__selected:
            properties = {key: self.__items[key] for key in self.__selected if key in self.__items}
        else:
            properties = {key: self.__items[key] for key in sorted(self.__items)}
        return cypher_repr(properties, **self.__kwargs)

    def __getattr__(self, key):
        if key in self.__selected:
            return self.__class__(self.__items, self.__selected)
        else:
            return self.__class__(self.__items, self.__selected + (key,))

    def __len__(self):
        return len(self.__items)

    def __iter__(self):
        return iter(self.__items)

    def __contains__(self, key):
        return key in self.__items


class PropertySelector(object):

    def __init__(self, items=(), default_value=None, **kwargs):
        self.__items = dict(items)
        self.__default_value = default_value
        self.__kwargs = kwargs

    def __getattr__(self, key):
        return cypher_str(self.__items.get(key, self.__default_value), **self.__kwargs)
