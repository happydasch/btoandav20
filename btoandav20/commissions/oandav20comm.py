from backtrader.comminfo import CommInfoBase


class OandaV20BacktestCommInfo(CommInfoBase):

    params = dict(
        spread=2.0,
        acc_counter_currency=True,
        pip_location=-4,
        automargin=False,
        margin=0.05,
        leverage=20.0,
        stocklike=False,
        commtype=CommInfoBase.COMM_FIXED,
    )

    def _getcommission(self, size, price, pseudoexec):
        '''
        This scheme will apply half the commission when buying and half when selling.
        If account currency is same as the base currency, change pip value calc.
        https://community.backtrader.com/topic/525/forex-commission-scheme
        '''
        multiplier = float(10 ** self.p.pip_location)
        if self.p.acc_counter_currency:
            comm = abs((self.p.spread * (size * multiplier)/2))
        else:
            comm = abs((self.p.spread * ((size / price) * multiplier)/2))
        return comm
