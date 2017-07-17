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
This module contains support for Cypher data types and values.
"""

from functools import reduce
from operator import xor as xor_operator

from cypy.collections import iter_items
from cypy.compat import integer_types, unicode_types, utf8_types, bytes_types, bstr, ustr


class Value(object):
    """ This class contains coercion methods for mapping Python values
    to Cypher values. Each Cypher type is normally represented by a
    particular Python type. These are:

    ===========  ==================
    Cypher Type  Normal Python Type
    ===========  ==================
    Null         :py:const:`None`
    Boolean      :py:attr:`bool`
    Integer      :py:attr:`int`
    Float        :py:attr:`float`
    String       :py:attr:`str` (or :py:attr:`unicode` in Python 2)
    Bytes        :py:attr:`bytearray`
    Map          :py:attr:`dict`
    List         :py:attr:`list`
    ===========  ==================

    All methods in this class are class methods as it is intended to act
    as a namespace and not an instance constructor.
    """

    nullable = True
    default_encoding = "utf-8"

    @classmethod
    def coerce(cls, value, encoding=None):
        """ Coerce a Python value to an appropriate Cypher value.

        The supported mappings are:

        =====================  ===============  ===========  =====
        Python Type            Python Versions  Cypher Type  Notes
        =====================  ===============  ===========  =====
        :py:const:`None`       2, 3+            Null
        :py:class:`bool`       2, 3+            Boolean
        :py:class:`int`        2, 3+            Integer      Must be in the range -(2\ :sup:`63`) to 2\ :sup:`63` - 1.
        :py:class:`long`       2                Integer      Must be in the range -(2\ :sup:`63`) to 2\ :sup:`63` - 1.
        :py:class:`float`      2, 3+            Float
        :py:class:`str`        2, 3+            String       In Python 2, a Unicode value is derived via the `encoding`.
        :py:class:`unicode`    2                String
        :py:class:`bytearray`  2, 3             Bytes
        :py:class:`bytes`      3                Bytes        In Python 2, :py:attr:`bytes` is an alias for :py:attr:`str`.
        :py:class:`dict`       2, 3             Map
        (iterable)             2, 3             List         Any other class which implements the :py:func:`__iter__` method.
        =====================  ===============  ===========  =====

        """
        if value is None:
            return cls.coerce_null(value)
        elif isinstance(value, bool):
            return cls.coerce_boolean(value)
        elif isinstance(value, integer_types):
            return cls.coerce_integer(value)
        elif isinstance(value, float):
            return cls.coerce_float(value)
        elif isinstance(value, unicode_types):
            return cls.coerce_string(value)
        elif isinstance(value, utf8_types):
            return cls.coerce_string(value, encoding)
        elif isinstance(value, bytes_types):
            return cls.coerce_bytes(value, encoding)
        elif isinstance(value, dict):
            return cls.coerce_map(value, encoding)
        elif hasattr(value, "__iter__"):
            return cls.coerce_list(value, encoding)
        else:
            raise TypeError("Values of type %s are not supported" % value.__class__.__name__)

    @classmethod
    def coerce_null(cls, _):
        """ Coerce a Python value to a Cypher Null.

        :returns: :py:const:`None`
        """
        if cls.nullable:
            return None
        else:
            raise ValueError("Null values are not supported")

    @classmethod
    def coerce_boolean(cls, value):
        """ Coerce a Python value to a Cypher Boolean.

        :rtype: :py:class:`bool`
        """
        return bool(value)

    @classmethod
    def coerce_integer(cls, value):
        """ Coerce a Python value to a Cypher Integer.

        :rtype: :py:class:`int`
        :raises ValueError: if out of range for a 64-bit signed integer
        """
        if (-2 ** 63) <= value < (2 ** 63):
            return int(value)
        else:
            raise ValueError("Integer value out of range: %s" % value)

    @classmethod
    def coerce_float(cls, value):
        """ Coerce a Python value to a Cypher Float.

        :rtype: :py:class:`float`
        """
        return float(value)

    @classmethod
    def coerce_bytes(cls, value, encoding=None):
        """ Coerce a Python value to Cypher Bytes.

        :rtype: :py:class:`bytearray`
        """
        return bstr(value, encoding or cls.default_encoding)

    @classmethod
    def coerce_string(cls, value, encoding=None):
        """ Coerce a Python value to a Cypher String.

        :rtype: :py:class:`str` (or :py:class:`unicode` in Python 2)
        """
        return ustr(value, encoding or cls.default_encoding)

    @classmethod
    def coerce_map(cls, value, encoding=None):
        """ Coerce a Python value to a Cypher Map.

        :rtype: :py:class:`dict`
        """
        if encoding is None:
            encoding = cls.default_encoding
        return {cls.coerce(key, encoding): cls.coerce(value, encoding) for key, value in value.items()}

    @classmethod
    def coerce_list(cls, value, encoding=None):
        """ Coerce a Python value to a Cypher List.

        :rtype: :py:class:`list`
        """
        return [cls.coerce(item, encoding or cls.default_encoding) for item in value]


class Record(tuple):
    """ A :class:`.Record` is an immutable ordered collection of key-value
    pairs. It is generally closer to a :py:class:`namedtuple` than to a
    :py:class:`OrderedDict` inasmuch as iteration of the collection will
    yield values rather than keys.
    """

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

    def __hash__(self):
        return reduce(xor_operator, map(hash, self.items()))

    def __getitem__(self, key):
        if isinstance(key, slice):
            keys = self.__keys[key]
            values = super(Record, self).__getitem__(key)
            return self.__class__(zip(keys, values))
        if isinstance(key, integer_types):
            index = key
        else:
            try:
                index = self.__keys.index(ustr(key))
            except ValueError:
                if self.value_class.nullable:
                    raise KeyError(key)
                else:
                    return None
        if 0 <= index < len(self) or self.value_class.nullable:
            return super(Record, self).__getitem__(index)
        else:
            return None

    def __getslice__(self, start, stop):
        key = slice(start, stop)
        keys = self.__keys[key]
        values = tuple(self)[key]
        return self.__class__(zip(keys, values))

    def get(self, key, default=None):
        try:
            index = self.__keys.index(ustr(key))
        except ValueError:
            return default
        if 0 <= index < len(self) or self.value_class.nullable:
            return super(Record, self).__getitem__(index)
        else:
            return default

    def keys(self):
        return self.__keys

    def values(self):
        return tuple(self)

    def items(self):
        return tuple((self.__keys[i], super(Record, self).__getitem__(i)) for i in range(len(self)))
