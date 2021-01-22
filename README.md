# btoandav20

Support for Oanda-V20 API in backtrader

**This  integration is still under development and may have some issues, use it for live trading at your own risk!**

## What is it

**btoandav20** is a package to integrate OANDA into [backtrader](https://www.backtrader.com/).
It uses the [v20](http://developer.oanda.com/rest-live-v20/introduction/) API of OANDA. It can be used with demo or live account.
We highly recommend to have a specific account to use backtrader with OANDA. You should not trade manually on the same account if you wish to use backtrader.

**It includes all necessary utilities to backtest or do live trading:**

* Store
* Broker
* Data Feeds
* Sizers
* Commissions

**Available features:**

* Accessing oandav20 API
* Streaming prices
* Streaming events
* Get *unlimited* history prices for backtesting
* Replay functionality for backtesting
* Replace pending orders
* Possibility to load existing positions from the OANDA account
* Reconnects on broken connections and after timeouts, also backfills data after a timeout or disconnect occurred

* **Support different type of orders:**
  * Order.Market
  * Order.Limit
  * Order.Stop
  * Order.StopTrail (by using brackets)
  * Bracket orders are supported by using the takeprofit and stoploss order members and creating internally simulated orders.

* **4 different OandaV20 Sizers:**
  * OandaV20PercentSizer - returns position size which matches the percent amount of total cash
  * OandaV20CashSizer - return position size which matches the cash amount
  * OandaV20RiskPercentSizer - returns position size which matches the total risk in percent of total amount (max stop loss)
  * OandaV2
  0RiskCashSizer - returns position size which matches the total risk in percent of total amount (max stop loss)

* **4 different backtest Sizers:**
  * OandaV20BacktestPercentSizer - returns position size which matches the percent amount of total cash
  * OandaV20BacktestCashSizer - return position size which matches the cash amount
  * OandaV20BacktestRiskPercentSizer - returns position size which matches the total risk in percent of total amount (max pips)
  * OandaV20BacktestRiskCashSizer - returns position size which matches the total risk in percent of total amount (max pips)

## Order Types

btoandav20 supports Market, Limit and Stop orders. Other order types, like StopTrail need to be created using brackets.

### StopTrail order

orderexec: bt.Order.Stop

stopexec: bt.Order.StopTrail

### Changing StopTrail order

To change a StopTrail order the stopside or takeside needs to be canceled and a new order with the order type StopTrail needs to be created.

Also an oref of the original order needs to be provided, when creating this order.
The order needs to go into the opposing direction.

**StopTrail example:**

Provide the stoptrail in stopargs with trailamount or trailpercent

* o, ostop, olimit = buy_bracket(exectype=bt.Order.Stop, stopexec=bt.Order.StopTrail, stopargs={"trailamount": xxx or "trailpercent": yyy} limitexec=None)

Create new trailing stop for parent order

* self.sell(exectype=bt.Order.StopTrail, trailamount=xxx or trailpercent=yyy, replace=ostop.ref)

## Dependencies

* python 3.6
* ``Backtrader`` (tested with version 1.9.61.122)
* ``pyyaml`` (tested with version 3.13)
* ``v20`` (tested with version 3.0.25) (<https://github.com/oanda/v20-python/releases>)

## Installation

The following steps have been tested on Mac OS High Sierra and Ubuntu 16 and 18.

1. Install backtrader ``pip install backtrader[plotting]`` (<https://www.backtrader.com/docu/installation.html>)
2. Install btoandav20 ``pip install git+https://github.com/happydasch/btoandav20``
   or with ``pipenv install git+https://github.com/happydasch/btoandav20#egg=btoandav20``

3. Import ``btoandav20`` into your script: ``import btoandav20`` (this is considering your script is at the root of your folder)

**You can then access the different parts such as:**

*Live:*

* Store: ``btoandav20.stores.OandaV20Store``
* Data Feed: ``btoandav20.feeds.OandaV20Data``
* Broker: ``btoandav20.brokers.OandaV20Broker``
* Sizers:
  * ``btoandav20.sizers.OandaV20PercentSizer``
  * ``btoandav20.sizers.OandaV20CashSizer``
  * ``btoandav20.sizers.OandaV20RiskPercentSizer``
  * ``btoandav20.sizers.OandaV20RiskCashSizer``

*Backtesting:*

* Sizers:
  * ``btoandav20.sizers.ForexPercentSizer``
  * ``btoandav20.sizers.ForexCashSizer``
  * ``btoandav20.sizers.ForexRiskPercentSizer``
  * ``btoandav20.sizers.ForexRiskCashSizer``
* Commissioninfo: ``btoandav20.commissions.OandaV20CommInfoBacktest``

If you encounter an issue during installation, please check this url first: <https://community.backtrader.com/topic/1570/oanda-data-feed/> and create a new issue if this doesn't solve it.

## Getting Started

See the [example](examples) folder for more detailed explanation on how to use it.

## Contribute

We are looking for contributors: if you are interested to join us please contact us.

## Sponsoring

If you want to support the development of btoandav20, consider to support this project.

* BTC: 39BJtPgUv6UMjQvjguphN7kkjQF65rgMMF
* ETH: 0x06d6f3134CD679d05AAfeA6e426f55805f9B395D
* https://liberapay.com/happydasch

## License

All code is based on backtrader oandastore which is released under GNU General Public License Version 3 by Daniel Rodriguez
