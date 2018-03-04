#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from backtrader.utils.py3 import (integer_types, queue, string_types,
                                  with_metaclass)
from backtrader import (TimeFrame, num2date, date2num, BrokerBase,
                        Order, BuyOrder, SellOrder, OrderBase, OrderData)
from btoandav20.stores import oandav20store


class MetaOandaV20Broker(BrokerBase.__class__):
    def __init__(cls, name, bases, dct):
        '''Class has already been created ... register'''
        # Initialize the class
        super(MetaOandaV20Broker, cls).__init__(name, bases, dct)
        # Register with the store
        oandav20store.OandaV20Store.BrokerCls = cls


class OandaV20Broker(with_metaclass(MetaOandaV20Broker, BrokerBase)):
    '''Broker implementation for Oanda v20.

    This class maps the orders/positions from Oanda to the
    internal API of ``backtrader``.

    Params:

      - ``use_positions`` (default:``True``): When connecting to the broker
        provider use the existing positions to kickstart the broker.

        Set to ``False`` during instantiation to disregard any existing
        position
    '''
    params = (
        ('use_positions', True),
    )

    def __init__(self, **kwargs):
        super(OandaV20Broker, self).__init__()
        self.o = oandav20store.OandaV20Store(**kwargs)

        self.startingcash = self.cash = 0.0
        self.startingvalue = self.value = 0.0

    def getcash(self):
        # This call cannot block if no answer is available from oanda
        self.cash = cash = self.o.get_cash()
        return cash

    def getvalue(self, datas=None):
        self.value = self.o.get_value()
        return self.value
