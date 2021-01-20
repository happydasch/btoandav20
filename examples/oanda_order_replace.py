import backtrader as bt
import btoandav20 as bto
import json

''' Test for orders from oanda '''


class St(bt.Strategy):

    params = {
        "order_type": bt.Order.StopTrail,
    }

    def __init__(self):
        self.order = None
        self.stop = None
        self.limit = None

    def notify_store(self, msg, *args, **kwargs):
        txt = ["*" * 5, "STORE NOTIF:", msg]
        print(", ".join(txt))

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.ref == self.order.ref:
                self.order = None
        txt = ["*" * 5, "ORDER NOTIF:", str(order)]
        print(", ".join(txt))

    def notify_trade(self, trade):
        txt = ["*" * 5, "TRADE NOTIF:", str(trade)]
        print(", ".join(txt))

    def next(self):

        if self.order:
            return

        if self.p.order_type == bt.Order.StopLimit:
            if not self.stop and not self.limit:
                price = self.data_close[0] + 0.0002
                self.order, self.stop, self.limit = self.buy_bracket(
                    size=1,
                    exectype=bt.Order.Stop,
                    price=price,
                    oargs={},
                    stopexec=None,
                    limitprice=price+0.001,
                    limitexec=bt.Order.StopLimit,
                    limitargs={})
            elif self.limit:
                price = self.data_close[0] + 0.002
                self.limit = self.sell(
                    exectype=bt.Order.StopLimit,
                    plimit=price,
                    replace=self.limit.ref)
        elif self.p.order_type == bt.Order.StopTrail:
            if not self.stop and not self.limit:
                price = self.data_close[0] + 0.0002
                self.order, self.stop, self.limit = self.buy_bracket(
                    size=1,
                    exectype=bt.Order.Stop,
                    price=price,
                    oargs={},
                    stopexec=bt.Order.StopTrail,
                    stopargs={
                        "trailamount": 0.0005
                    },
                    limitexec=None,)
            elif self.stop:
                self.stop = self.sell(
                    exectype=bt.Order.StopTrail,
                    trailamount=0.001,
                    replace=self.stop.ref)


with open("config.json", "r") as file:
    config = json.load(file)

storekwargs = dict(
    token=config["oanda"]["token"],
    account=config["oanda"]["account"],
    practice=config["oanda"]["practice"],
    notif_transactions=True,
    stream_timeout=10,
)
store = bto.stores.OandaV20Store(**storekwargs)
datakwargs = dict(
    timeframe=bt.TimeFrame.Minutes,
    compression=1,
    tz='Europe/Berlin',
    backfill=False,
    backfill_start=False,
)
data = store.getdata(dataname="EUR_USD", **datakwargs)
data.resample(
    timeframe=bt.TimeFrame.Minutes,
    compression=1)  # rightedge=True, boundoff=1)
cerebro = bt.Cerebro()
cerebro.adddata(data)
cerebro.setbroker(store.getbroker())
cerebro.addstrategy(St)
cerebro.run()
