import backtrader as bt


'''
https://www1.oanda.com/lang/en/forex-trading/analysis/currency-units-calculator
'''


class ForexSizer(bt.Sizer):

    params = dict(
        percents=0,   # percents of cash
        amount=0,     # amount of cash
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if position:
            return position.size
        cash = self.broker.getcash()
        price = data.close[0]
        avail = comminfo.getsize(price, cash)
        if self.p.percents != 0:
            size = avail * (self.p.percents / 100)
        elif self.p.amount != 0:
            size = (avail / cash) * self.p.amount
        else:
            size = 0
        return int(size)


class ForexPercentSizer(ForexSizer):

    params = dict(
        percents=5,
    )


class ForexCashSizer(ForexSizer):

    params = dict(
        amount=50,
    )


class ForexRiskSizer(bt.Sizer):

    params = dict(
        percents=0,   # risk percents
        amount=0,     # risk amount
        stoploss=5,   # stop loss in pips
    )

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
        cash = self.broker.getcash()
        price = data.close[0]
        avail = comminfo.getsize(price, cash)
        if self.p.percents != 0:
            cash_to_use = cash * (self.p.percents/100)
        elif self.p.amount != 0:
            cash_to_use = self.p.amount
        price_per_pip = cash_to_use / stoploss
        size = price_per_pip * (avail / cash)
        size *= comminfo.get_leverage()
        return int(size)


class ForexRiskPercentSizer(ForexRiskSizer):

    params = dict(
        percents=5,
    )


class ForexRiskCashSizer(ForexRiskSizer):

    params = dict(
        amount=50,
    )
