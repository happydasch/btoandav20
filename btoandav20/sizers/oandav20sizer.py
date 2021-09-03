from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
from btoandav20.stores import oandav20store


class OandaV20Sizer(bt.Sizer):

    params = dict(
        percents=0,   # percents of cash
        amount=0,     # fixed amount
        avail_reduce_perc=0,
    )

    def __init__(self, **kwargs):
        super(OandaV20Sizer, self).__init__(**kwargs)
        self.o = oandav20store.OandaV20Store(**kwargs)

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if position:
            return position.size

        name = data.contractdetails['name']
        sym_src = self.o.get_currency()
        sym_to = name[-(len(sym_src)):]

        cash_to_use = 0
        if self.p.percents != 0:
            cash_to_use = cash * (self.p.percents / 100)
        elif self.p.amount != 0:
            cash_to_use = self.p.amount
        if self.p.avail_reduce_perc > 0:
            cash_to_use -= cash_to_use / 100 * self.p.avail_reduce_perc

        price = self.o.get_pricing(name)
        if not price:
            return 0
        if sym_src != sym_to:
            # convert cash to target currency
            convprice = self.o.get_pricing(sym_src + '_' + sym_to)
            if convprice:
                cash_to_use = (
                    cash_to_use
                    / (1 / float(convprice['closeoutAsk'])))

        if self.p.percents != 0:
            size = avail * (self.p.percents / 100)
        elif self.p.amount != 0:
            size = cash_to_use * (self.p.amount / cash)
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
        pips=10,      # stop loss in pips
        avail_reduce_perc=0,
    )

    def __init__(self, **kwargs):
        super(OandaV20RiskSizer, self).__init__(**kwargs)
        self.o = oandav20store.OandaV20Store(**kwargs)

    def getsizing(self, data, isbuy, pips=None):
        comminfo = self.broker.getcommissioninfo(data)
        return self._getsizing(
            comminfo,
            self.broker.getcash(),
            data,
            isbuy,
            pips)

    def _getsizing(self, comminfo, cash, data, isbuy, pips=None):
        if not pips:
            pips = self.p.pips
        position = self.broker.getposition(data)
        if position:
            return position.size

        name = data.contractdetails['name']
        sym_src = self.o.get_currency()
        sym_to = name[-(len(sym_src)):]

        cash_to_use = 0
        if self.p.percents != 0:
            cash_to_use = cash * (self.p.percents / 100)
        elif self.p.amount != 0:
            cash_to_use = self.p.amount
        if self.p.avail_reduce_perc > 0:
            cash_to_use -= cash_to_use / 100 * self.p.avail_reduce_perc

        price = self.o.get_pricing(name)
        if not price:
            return 0
        if sym_src != sym_to:
            # convert cash to target currency
            convprice = self.o.get_pricing(sym_src + '_' + sym_to)
            if convprice:
                cash_to_use = (
                    cash_to_use
                    / (1 / float(convprice['closeoutAsk'])))

        price_per_pip = cash_to_use / pips
        mult = float(1 / 10 ** data.contractdetails['pipLocation'])
        size = price_per_pip * mult
        return int(size)


class OandaV20RiskPercentSizer(OandaV20RiskSizer):

    params = dict(
        percents=5,
    )


class OandaV20RiskCashSizer(OandaV20RiskSizer):

    params = dict(
        amount=50,
    )
