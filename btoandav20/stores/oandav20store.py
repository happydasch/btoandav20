#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

import backtrader as bt
from backtrader.metabase import MetaParams
from backtrader.utils.py3 import queue, with_metaclass


class MetaSingleton(MetaParams):
    '''Metaclass to make a metaclassed class a singleton'''
    def __init__(cls, name, bases, dct):
        super(MetaSingleton, cls).__init__(name, bases, dct)
        cls._singleton = None

    def __call__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = (
                super(MetaSingleton, cls).__call__(*args, **kwargs))

        return cls._singleton


class OandaV20Store(with_metaclass(MetaSingleton, object)):

    params = (
        ('token', ''),
        ('account', ''),
        ('practice', False),
        ('account_tmout', 10.0),  # account balance refresh timeout
    )

    def __init__(self):
        super(OandaV20Store, self).__init__()

    def start(self, data=None, broker=None):
        raise Exception("Not implemented")

    def stop(self):
        raise Exception("Not implemented")

    def put_notification(self, msg, *args, **kwargs):
        raise Exception("Not implemented")

    def get_notifications(self):
        raise Exception("Not implemented")

    def get_positions(self):
        raise Exception("Not implemented")

    def get_granularity(self, timeframe, compression):
        raise Exception("Not implemented")

    def get_instrument(self, dataname):
        raise Exception("Not implemented")

    def streaming_events(self, tmout=None):
        raise Exception("Not implemented")

    def candles(self, dataname, dtbegin, dtend, timeframe, compression,
                candleFormat, includeFirst):
        raise Exception("Not implemented")

    def streaming_prices(self, dataname, tmout=None):
        raise Exception("Not implemented")

    def get_cash(self):
        raise Exception("Not implemented")

    def get_value(self):
        raise Exception("Not implemented")

    def broker_threads(self):
        raise Exception("Not implemented")

    def order_create(self, order, stopside=None, takeside=None, **kwargs):
        raise Exception("Not implemented")

    def order_cancel(self, order):
        raise Exception("Not implemented")
