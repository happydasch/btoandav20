import backtrader as bt


class ForexSizer(bt.Sizer):

    params = (
        ('percents', 0),   # percents of cash
        ('amount', 0),  # amount of cash
        ('acc_counter_currency', True),  # is account in counter currency
    )

    def _getmaxavailable(self, data, comminfo):
        # https://www1.oanda.com/lang/en/forex-trading/analysis/currency-units-calculator
        avail = self.broker.getcash() * comminfo.get_leverage()
        if not self.p.acc_counter_currency:
            avail = avail / data.close[0]
        return avail

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if position:
            return position.size
        avail = self._getmaxavailable(data, comminfo)
        if self.p.percents != 0:
            size = avail * (self.p.percents / 100)
        elif self.p.amount != 0:
            size = (avail / cash) * self.p.amount
        else:
            size = 0
        return int(size)


class ForexPercentSizer(ForexSizer):

    params = (
        ('percents', 5),
    )


class ForexCashSizer(ForexSizer):

    params = (
        ('amount', 50),
    )


class ForexRiskSizer(bt.Sizer):

    params = (
        ('percents', 0),   # percents of cash
        ('stoploss', 5),  # stop loss in pips
        ('amount', 0),     # risk amount
        ('acc_counter_currency', True),  # is account in counter currency
    )

    def _getmaxavailable(self, data, comminfo):
        # https://www1.oanda.com/lang/en/forex-trading/analysis/currency-units-calculator
        avail = self.broker.getcash() * comminfo.get_leverage()
        if not self.p.acc_counter_currency:
            avail = avail / data.close[0]
        return avail

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
        price = data.close[0]
        cash = self.broker.getcash()
        if self.p.percents != 0:
            cash_to_use = cash * (self.p.percents/100)
        elif self.p.amount != 0:
            cash_to_use = self.p.amount
        price_per_pip = cash_to_use / stoploss
        size = price_per_pip * cash
        if not self.p.acc_counter_currency:
            size = size / price
        size = min(size, self._getmaxavailable(
            data,
            comminfo))
        return int(size)


class ForexRiskPercentSizer(ForexRiskSizer):

    params = (
        ('percents', 5),
    )


class ForexRiskCash(ForexRiskSizer):

    params = (
        ('amount', 50),
    )
