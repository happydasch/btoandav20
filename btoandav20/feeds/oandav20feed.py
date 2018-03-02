#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from backtrader.utils.py3 import (integer_types, queue, string_types,
                                  with_metaclass)
from backtrader.feed import DataBase
from btoandav20.stores import oandav20store


class MetaOandaV20Data(DataBase.__class__):
    def __init__(cls, name, bases, dct):
        '''Class has already been created ... register'''
        # Initialize the class
        super(MetaOandaV20Data, cls).__init__(name, bases, dct)
        # Register with the store
        oandav20store.OandaV20Store.DataCls = cls


class OandaV20Data(with_metaclass(MetaOandaV20Data, DataBase)):

    _store = oandav20store.OandaV20Store

    def __init__(self, **kwargs):
        self.o = self._store(**kwargs)

