from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
from btoandav20.stores import oandav20store


class OandaV20Sizer(bt.Sizer):

    params = dict(
        percents=0,   # percents of cash
        amount=0,     # fixed amount
    )

    def __init__(self, **kwargs):
        super(OandaV20Sizer, self).__init__(**kwargs)
        self.o = oandav20store.OandaV20Store(**kwargs)

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if position:
            return position.size

        avail = 0
        name = data.contractdetails['name']
        price = self.o.get_pricing(name)
        if price is not None:
            if isbuy:
                avail = float(price['unitsAvailable']['default']['long'])
            else:
                avail = float(price['unitsAvailable']['default']['short'])
        if self.p.percents != 0:
            size = avail * (self.p.percents / 100)
        elif self.p.amount != 0:
            size = (avail / cash) * self.p.amount
        else:
            size = 0
        return int(size)


class OandaV20PercentSizer(OandaV20Sizer):

    params = dict(
        percents=5,
    )


class OandaV20CashSizer(OandaV20Sizer):

    params = dict(
        amount=50,
    )


class OandaV20RiskSizer(bt.Sizer):

    params = dict(
        percents=0,   # risk percents
        amount=0,     # risk amount
        stoploss=10,  # stop loss in pips
    )

    def __init__(self, **kwargs):
        super(OandaV20RiskSizer, self).__init__(**kwargs)
        self.o = oandav20store.OandaV20Store(**kwargs)

    def getsizing(self, data, isbuy, stoploss=None):
        comminfo = self.broker.getcommissioninfo(data)
        return self._getsizing(
            comminfo,
            self.broker.getcash(),
            data,
            isbuy,
            stoploss)

    def _getsizing(self, comminfo, cash, data, isbuy, stoploss=None):
        if not stoploss:
            stoploss = self.p.stoploss
        position = self.broker.getposition(data)
        if position:
            return position.size

        name = data.contractdetails['name']

        sym_to = name[4:]
        sym_src = self.o.get_currency()

        cash_to_use = 0
        if self.p.percents != 0:
            cash_to_use = cash * (self.p.percents / 100)
        elif self.p.amount != 0:
            cash_to_use = self.p.amount

        if sym_src != sym_to:
            # convert cash to target currency
            price = self.o.get_pricing(sym_src + '_' + sym_to)
            if price is not None:
                cash_to_use = cash_to_use / (1 / float(price['closeoutAsk']))

        size = 0
        price_per_pip = cash_to_use / stoploss
        price = self.o.get_pricing(name)
        if price is not None:
            size = (
                price_per_pip
                * (1 / 10 ** data.contractdetails['pipLocation']))
            if isbuy:
                size = min(
                    size,
                    float(price['unitsAvailable']['default']['long']))
            else:
                size = min(
                    size,
                    float(price['unitsAvailable']['default']['short']))

        return int(size)


class OandaV20RiskPercentSizer(OandaV20RiskSizer):

    params = dict(
        percents=5,
    )


class OandaV20RiskCashSizer(OandaV20RiskSizer):

    params = dict(
        amount=50,
    )
