# backtrader-oandav20

[![Build Status](https://travis-ci.org/ftomassetti/backtrader-oandav20.svg?branch=master)](https://travis-ci.org/ftomassetti/backtrader-oandav20)

Support for Oanda-V20 API in backtrader

**This  integration is still under development and may have some issues, use it for live trading at your own risk!**

**We are looking for contributors: if you are interested to join us please contact us**



## What is it ?

**backtrader-oandav20** is a package to integrate OANDA into [backtrader](https://www.backtrader.com/).
It uses the [v20](http://developer.oanda.com/rest-live-v20/introduction/) API of OANDA. It can be used with demo or live account.
We highly recommend to have a specific account to use backtrader with OANDA. You should not trade manually on the same account if you wish to use backtrader.


It includes all necessary utilities to backtest or do live trading:

* Store
* Broker
* Data Feeds
* Sizers

Available features:

* Accessing oandav20 API
* Streaming prices
* Streaming events
* Get *unlimited* history prices for backtesting
* Replay functionality for backtesting
* Support different type of orders:
  * Order.Market
  * Order.Limit
  * Order.Stop
  * Order.StopLimit (using Stop and upperBound / lowerBound prices) *may not be possible*
  * Order.StopTrail (will only work in buy and sell brackets)
  * Bracket orders are supported by using the takeprofit and stoploss order members and creating internally simulated orders.
* 4 different Sizers:
  * OandaV20Percent - returns position size which matches the percent amount of total cash
  * OandaV20Cash - return position size which matches the cash amount
  * OandaV20RiskPercent - returns position size which matches the total risk in percent of total amount (max stop loss)
  * OandaV20RiskCash - returns position size which matches the total risk in percent of total amount (max stop loss)
* Possibility to load existing positions from the OANDA account



## Required dependencies

* python 3.6
* ``Backtrader`` (tested with version 1.9.61.122)
* ``pyyaml`` (tested with version 3.13)
* ``v20`` (tested with version 3.0.25) (https://github.com/oanda/v20-python/releases)



## Installation

The following steps have been tested on Mac OS High Sierra and Ubuntu 16 and 18.

1. Install backtrader ``pip install backtrader[plotting]`` (https://www.backtrader.com/docu/installation.html)
2. Install backtrader-oandav20 ``pip install https://github.com/ftomassetti/backtrader-oandav20``
3. Install dependencies:
    * ``pip install pyyaml``
    * ``pip install v20``
4. Import ``btoandav20`` into your script: ``import btoandav20`` (this is considering your script is at the root of your folder)
5. You can then access the different such as :
    * Store: ``btoandav20.stores.OandaV20Store``
    * Data Feed: ``btoandav20.feeds.OandaV20Data``
    * Broker:  ``btoandav20.brokers.OandaV20Broker``
    * Sizers: ``btoandav20.sizers.OandaV20Cash`` (other sizers are available)

If you encounter an issue during installation, please check this url first: https://community.backtrader.com/topic/1570/oanda-data-feed/13 and create a new issue if this doesn't solve it.



## Get Started
See the [example](examples/oandav20test) folder for more detailed explanation on how to use it.



## License

All code is based on backtrader oandastore which is released under GNU General Public License Version 3 by Daniel Rodriguez
