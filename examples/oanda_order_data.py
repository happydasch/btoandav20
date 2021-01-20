import backtrader as bt
import btoandav20 as bto
import json

''' Order info '''


class St(bt.Strategy):

    def __init__(self):
        self.order = None

    def notify_store(self, msg, *args, **kwargs):
        if "clientExtensions" in msg:
            o_info = json.loads(msg["clientExtensions"]["comment"]

    def next(self):
        if self.order:
            return
        self.buy(exectype=bt.Order.Limit, price=price, size=1)

with open("config/config.json", "r") as file:
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
