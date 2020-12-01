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

    def __init__(self):
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
        multiplier = float(10 ** self.p.pip_location)
        if self.p.acc_counter_currency:
            comm = abs(
                self.p.spread * (size * multiplier))
        else:
            comm = abs(
                self.p.spread * ((size / price) * multiplier))
        return comm / 2
