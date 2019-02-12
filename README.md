# backtrader-oandav20

[![Build Status](https://travis-ci.org/ftomassetti/backtrader-oandav20.svg?branch=master)](https://travis-ci.org/ftomassetti/backtrader-oandav20)

Support for Oanda-V20 API in backtrader  

**This  integration is still under development and may have some issues, use it for live trading at your own risk!**

**We are looking for contributors: if you are interested to join us please contact us**

## What is it ?

**backtrader-oandav20** is a package to integrate OANDA into backtrader (https://www.backtrader.com/).
It includes all necessary utilities to backtest or trade using an OANDA account:

* Store
* Broker
* Data Feeds from OANDA (history as well as live streamming)
* Sizers 

## Required dependencies

* python 3.6 (not tested with other version)
* "Backtrader" 1.9.61.122+
* "pyyaml" version 3.13+ 
* "v20" 3.0.25+ (https://github.com/oanda/v20-python/releases)

## Installation

No package is available at the moment so you need to install it manually.

1. Download a zip file of the master branch
2. Extract the zip files
3. Copy the btoandav20 into your own working directory
4. Install dependencies (see above)
5. Import btoandav20 into your script: ``import btoandav20``
6. You can then access the different such as :
  * Store: ``btoandav20.stores.OandaV20Store`` 
  * Data Feed: ``btoandav20.feeds.OandaV20Data`` 
  * Broker:  ``btoandav20.brokers.OandaV20Broker``
  * Sizers: ``btoandav20.sizers.OandaV20Cash`` (other sizers are available)

## Get Started  
See the **examples** folder for more detailed explanation on how to use it. 
 

## Development

Python 3.6 is used.

## License

All code is based on backtrader oandastore which is released under GNU General Public License Version 3 by Daniel Rodriguez
