from backtrader.comminfo import CommInfoBase


class OandaV20BacktestCommInfo(CommInfoBase):

    params = dict(
        spread=0.0,
        acc_counter_currency=True,
        pip_location=-4,
        margin=0.5,
        leverage=20.0,
        stocklike=False,
        commtype=CommInfoBase.COMM_FIXED,
    )

    def __init__(self, data=None):
        self.data = data
        if self.p.stocklike:
            raise Exception('Stocklike is not supported')
        super(OandaV20BacktestCommInfo, self).__init__()

    def getsize(self, price, cash):
        '''Returns the needed size to meet a cash operation at a given price'''
        size = super(OandaV20BacktestCommInfo, self).getsize(price, cash)
        size *= self.p.margin
        if not self.p.acc_counter_currency:
            size /= price
        return int(size)

    def _getcommission(self, size, price, pseudoexec):
        '''
        This scheme will apply half the commission when buying and half when selling.
        If account currency is same as the base currency, change pip value calc.
        https://community.backtrader.com/topic/525/forex-commission-scheme
        '''
        if (self.data is not None
                and hasattr(self.data.l, 'bid_close')
                and hasattr(self.data.l, 'ask_close')
                and hasattr(self.data.l, 'mid_close')):
            if size > 0:
                spread = self.data.l.mid_close[0] - self.data.l.bid_close[0]
            else:
                spread = self.data.l.ask_close[0] - self.data.l.mid_close[0]
        else:
            spread = self.p.spread
        multiplier = float(10 ** self.p.pip_location)
        if self.p.acc_counter_currency:
            comm = abs(spread * (size * multiplier))
        else:
            comm = abs(spread * ((size / price) * multiplier))
        return comm / 2
