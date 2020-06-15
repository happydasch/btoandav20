from backtrader.comminfo import CommInfoBase


class OandaV20CommInfoBacktest(CommInfoBase):

    params = dict(
        spread=2.0,
        stocklike=False,
        pip_location=-4,
        acc_counter_currency=True,
        automargin=1.00,
        leverage=1,
        mult=1,
        commtype=CommInfoBase.COMM_FIXED,
    )

    def getvaluesize(self, size, price):
        # In real life the margin approaches the price
        return abs(size) * price

    def getoperationcost(self, size, price):
        '''Returns the needed amount of cash an operation would cost'''
        # Same reasoning as above
        return abs(size) * price

    def _getcommission(self, size, price, pseudoexec):
        '''
        This scheme will apply half the commission when buying and half when selling.
        If account currency is same as the base currency, change pip value calc.
        https://community.backtrader.com/topic/525/forex-commission-scheme
        '''
        multiplier = float(10 ** self.p.pip_location)
        comm = abs((self.p.spread * ((size / price) * multiplier)/2))
        return comm
