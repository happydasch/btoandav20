#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
from btoandav20.stores import oandav20store

class OandaV20Sizer(bt.Sizer):

    params = (
        ('percents', 0),   # percents of cash
        ('amount', 0),     # fixed amount
    )

    def __init__(self, **kwargs):
        self.o = oandav20store.OandaV20Store(**kwargs)

    def _getsizing(self, comminfo, cash, data, isbuy):
        avail = 0
        name = data.contractdetails['name']
        price = self.o.get_pricing(name)
        if price is not None:
            if isbuy:
                avail = float(price['unitsAvailable']['default']['long'])
            else:
                avail = float(price['unitsAvailable']['default']['short'])
        if self.p.percents is not 0:
            size = avail * (self.p.percents / 100)
            print(avail, self.p.percents)
        elif self.p.amount is not 0:
            size = (avail / cash) * self.p.amount
        else:
            size = 0
        return size

class OandaV20Percent(OandaV20Sizer):

    params = (
        ('percents', 20),
    )

class OandaV20Cash(OandaV20Sizer):

    params = (
        ('amount', 50),
    )
