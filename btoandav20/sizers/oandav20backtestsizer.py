import backtrader as bt

from btoandav20.commissions import OandaV20BacktestCommInfo


class OandaV20BacktestSizer(bt.Sizer):

    params = dict(
        percents=0,   # percents of cash
        amount=0,     # amount of cash
        avail_reduce_perc=0,
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if position:
            return position.size
        price = data.close[0]
        avail = comminfo.getsize(price, cash)
        if self.p.avail_reduce_perc > 0:
            avail -= avail/100 * self.p.avail_reduce_perc
        if self.p.percents != 0:
            size = avail * (self.p.percents / 100)
        elif self.p.amount != 0:
            size = (avail / cash) * self.p.amount
        else:
            size = 0
        return int(size)


class OandaV20BacktestPercentSizer(OandaV20BacktestSizer):

    params = dict(
        percents=5,
    )


class OandaV20BacktestCashSizer(OandaV20BacktestSizer):

    params = dict(
        amount=50,
    )


class OandaV20BacktestRiskSizer(bt.Sizer):

    params = dict(
        percents=0,   # risk percents
        amount=0,     # risk amount
        pips=5,   # stop loss in pips
        avail_reduce_perc=0,
    )

    def getsizing(self, data, isbuy, pips=None, price=None,
                  exchange_rate=None):
        comminfo = self.broker.getcommissioninfo(data)
        return self._getsizing(
            comminfo, self.broker.getvalue(),
            data, isbuy, pips, price, exchange_rate)

    def _getsizing(self, comminfo, cash, data, isbuy, pips=None,
                   price=None, exchange_rate=None):
        position = self.broker.getposition(data)
        if position:
            return position.size
        if not pips:
            pips = self.p.pips
        price = data.close[0]
        avail = comminfo.getsize(price, cash)
        if self.p.avail_reduce_perc > 0:
            avail -= avail/100 * self.p.avail_reduce_perc
        if self.p.percents != 0:
            cash_to_use = cash * (self.p.percents/100)
        elif self.p.amount != 0:
            cash_to_use = self.p.amount
        else:
            raise Exception('Either percents or amount is needed')
        if not isinstance(comminfo, OandaV20BacktestCommInfo):
            raise Exception('OandaV20CommInfo required')

        mult = float(1/10 ** comminfo.p.pip_location)
        price_per_pip = cash_to_use / pips
        if not comminfo.p.acc_counter_currency and price:
            # Acc currency is same as base currency
            pip = price_per_pip * price
            size = pip * mult
        elif exchange_rate:
            # Acc currency is neither same as base or counter currency
            pip = price_per_pip * exchange_rate
            size = pip * mult
        else:
            # Acc currency and counter currency are the same
            size = price_per_pip * mult
        size = min(size, avail)
        return int(size)


class OandaV20BacktestRiskPercentSizer(OandaV20BacktestRiskSizer):

    params = dict(
        percents=5,
    )


class OandaV20BacktestRiskCashSizer(OandaV20BacktestRiskSizer):

    params = dict(
        amount=50,
    )
