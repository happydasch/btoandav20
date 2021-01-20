import backtrader as bt
import btoandav20 as bto
import json

''' Test for orders from oanda '''


class St(bt.Strategy):

    params = dict(
        order_type=bt.Order.Stop,
        use_brackets=True,
        sell=False
    )

    def __init__(self):
        self.order = None

    def notify_store(self, msg, *args, **kwargs):
        txt = ["*" * 5, "STORE NOTIF:", msg]
        print(", ".join(txt))

    def notify_order(self, order):
        txt = ["*" * 5, "ORDER NOTIF:", str(order)]
        print(", ".join(txt))

    def notify_trade(self, trade):
        txt = ["*" * 5, "TRADE NOTIF:", str(trade)]
        print(", ".join(txt))

    def next(self):

        if self.order:
            return

        # create a market order
        if self.p.order_type == bt.Order.Market:
            price = self.data.close[0]
            if self.p.use_brackets:
                if self.p.sell:
                    self.order, _, _ = self.sell_bracket(
                        size=1, exectype=bt.Order.Market,
                        oargs={},
                        stopprice=price + 0.0002,
                        stopexec=bt.Order.Stop,
                        stopargs={},
                        limitprice=price - 0.0002,
                        limitexec=bt.Order.Limit,
                        limitargs={})
                else:
                    self.order, _, _ = self.buy_bracket(
                        size=1, exectype=bt.Order.Market,
                        oargs={},
                        stopprice=price - 0.0002,
                        stopexec=bt.Order.Stop,
                        stopargs={},
                        limitprice=price + 0.0002,
                        limitexec=bt.Order.Limit,
                        limitargs={})
            else:
                if self.p.sell:
                    self.order = self.sell(exectype=bt.Order.Market, size=1)
                else:
                    self.order = self.buy(exectype=bt.Order.Market, size=1)
        elif self.p.order_type == bt.Order.Limit:
            price = self.data.close[0]
            if self.p.use_brackets:
                if self.p.sell:
                    self.order, _, _ = self.sell_bracket(
                        size=1,
                        exectype=bt.Order.Limit,
                        price=price,
                        oargs={},
                        stopprice=price + 0.0005,
                        stopexec=bt.Order.Stop,
                        stopargs={},
                        limitprice=price - 0.0005,
                        limitexec=bt.Order.Limit,
                        limitargs={})
                else:
                    self.order, _, _ = self.buy_bracket(
                        size=1,
                        exectype=bt.Order.Limit,
                        price=price,
                        oargs={},
                        stopprice=price - 0.0005,
                        stopexec=bt.Order.Stop,
                        stopargs={},
                        limitprice=price + 0.0005,
                        limitexec=bt.Order.Limit,
                        limitargs={})
            else:
                if self.p.sell:
                    self.order = self.sell(exectype=bt.Order.Limit, price=price, size=1)
                else:
                    self.order = self.buy(exectype=bt.Order.Limit, price=price, size=1)
        elif self.p.order_type == bt.Order.Stop:
            price = self.data.close[0]
            if self.p.use_brackets:
                if self.p.sell:
                    self.order, _, _ = self.sell_bracket(
                        size=1,
                        exectype=bt.Order.Stop,
                        price=price,
                        oargs={},
                        stopprice=price + 0.0002,
                        stopexec=bt.Order.Stop,
                        stopargs={},
                        limitprice=price - 0.0002,
                        limitexec=bt.Order.Limit,
                        limitargs={})
                else:
                    self.order, _, _ = self.buy_bracket(
                        size=1,
                        exectype=bt.Order.Stop,
                        price=price,
                        oargs={},
                        stopprice=price - 0.0005,
                        stopexec=bt.Order.Stop,
                        stopargs={},
                        limitprice=price + 0.0005,
                        limitexec=bt.Order.Limit,
                        limitargs={})
            else:
                if self.p.sell:
                    self.order = self.sell(exectype=bt.Order.Stop, price=price, size=1)
                else:
                    self.order = self.buy(exectype=bt.Order.Stop, price=price, size=1)


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
    timeframe=bt.TimeFrame.Seconds,
    compression=30,
    tz='Europe/Berlin',
    backfill=False,
    backfill_start=False,
)
data = store.getdata(dataname="EUR_USD", **datakwargs)
data.resample(
    timeframe=bt.TimeFrame.Seconds,
    compression=30)  # rightedge=True, boundoff=1)
cerebro = bt.Cerebro()
cerebro.adddata(data)
cerebro.setbroker(store.getbroker())
cerebro.addstrategy(St)
cerebro.run()
