#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import collections
import json
import threading
import time as _time
from datetime import datetime, timedelta

import v20

import backtrader as bt
from backtrader.metabase import MetaParams
from backtrader.utils.py3 import queue, with_metaclass


class MetaSingleton(MetaParams):
    '''Metaclass to make a metaclassed class a singleton'''
    def __init__(cls, name, bases, dct):
        super(MetaSingleton, cls).__init__(name, bases, dct)
        cls._singleton = None

    def __call__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = (
                super(MetaSingleton, cls).__call__(*args, **kwargs))

        return cls._singleton


class OandaV20Store(with_metaclass(MetaSingleton, object)):
    '''Singleton class wrapping to control the connections to Oanda v20.

    Params:

      - ``token`` (default:``None``): API access token

      - ``account`` (default: ``None``): account id

      - ``practice`` (default: ``False``): use the test environment

      - ``account_tmout`` (default: ``10.0``): refresh period for account
        value/cash refresh
    '''

    params = (
        ('token', ''),
        ('account', ''),
        ('practice', False),
        ('account_tmout', 10.0),  # account balance refresh timeout
    )

    BrokerCls = None  # broker class will auto register
    DataCls = None  # data class will auto register

    _DTEPOCH = datetime(1970, 1, 1)

    # Oanda supported granularities
    _GRANULARITIES = {
        (bt.TimeFrame.Seconds, 5): 'S5',
        (bt.TimeFrame.Seconds, 10): 'S10',
        (bt.TimeFrame.Seconds, 15): 'S15',
        (bt.TimeFrame.Seconds, 30): 'S30',
        (bt.TimeFrame.Minutes, 1): 'M1',
        (bt.TimeFrame.Minutes, 2): 'M3',
        (bt.TimeFrame.Minutes, 3): 'M3',
        (bt.TimeFrame.Minutes, 4): 'M4',
        (bt.TimeFrame.Minutes, 5): 'M5',
        (bt.TimeFrame.Minutes, 10): 'M10',
        (bt.TimeFrame.Minutes, 15): 'M15',
        (bt.TimeFrame.Minutes, 30): 'M30',
        (bt.TimeFrame.Minutes, 60): 'H1',
        (bt.TimeFrame.Minutes, 120): 'H2',
        (bt.TimeFrame.Minutes, 180): 'H3',
        (bt.TimeFrame.Minutes, 240): 'H4',
        (bt.TimeFrame.Minutes, 360): 'H6',
        (bt.TimeFrame.Minutes, 480): 'H8',
        (bt.TimeFrame.Days, 1): 'D',
        (bt.TimeFrame.Weeks, 1): 'W',
        (bt.TimeFrame.Months, 1): 'M',
    }

    # Order type matching with oanda
    _ORDEREXECS = {
        bt.Order.Market: 'market',
        bt.Order.Limit: 'limit',
        bt.Order.Stop: 'stop',
        bt.Order.StopLimit: 'stop',
    }

    # oid fields to look for
    _OIDSINGLE = ['orderOpened',
                  'tradeOpened',
                  'tradeReduced']
    _OIDMULTIPLE = ['tradesClosed']

    _X_ORDER_CREATE = ('STOP_ORDER_CREATE',
                       'LIMIT_ORDER_CREATE',
                       'MARKET_IF_TOUCHED_ORDER_CREATE',)

    _X_ORDER_FILLED = ('MARKET_ORDER_CREATE',
                       'ORDER_FILLED',
                       'TAKE_PROFIT_FILLED',
                       'STOP_LOSS_FILLED',
                       'TRAILING_STOP_FILLED',)

    # Oanda api endpoints
    _OAPI_URL = ["api-fxtrade.oanda.com",
                 "api-fxpractice.oanda.com"]
    _OAPI_STREAM_URL = ["stream-fxtrade.oanda.com",
                        "stream-fxpractice.oanda.com"]


    @classmethod
    def getdata(cls, *args, **kwargs):
        '''Returns ``DataCls`` with args, kwargs'''
        return cls.DataCls(*args, **kwargs)

    @classmethod
    def getbroker(cls, *args, **kwargs):
        '''Returns broker with *args, **kwargs from registered ``BrokerCls``'''
        return cls.BrokerCls(*args, **kwargs)

    def __init__(self):
        super(OandaV20Store, self).__init__()

        self.notifs = collections.deque()  # store notifications for cerebro

        self._cash = 0.0 # margin available, currently available cash
        self._value = 0.0 # account balance
        self._currency = None # account currency
        self._marginRate = 1.0 # margin rate / leverage

        self._env = None  # reference to cerebro for general notifications
        self._evt_acct = threading.Event()

        self.broker = None  # broker instance
        self.datas = list()  # datas that have registered over start

        self._orders = collections.OrderedDict()  # map order.ref to oid
        self._ordersrev = collections.OrderedDict()  # map oid to order.ref
        self._transpend = collections.defaultdict(collections.deque)

        # init oanda v20 api context
        self.oapi = v20.Context(
            self._OAPI_URL[int(self.p.practice)],
            port=443,
            ssl=True,
            token=self.p.token,
            datetime_format="UNIX",
        )

        # init oanda v20 api stream context
        self.oapi_stream = v20.Context(
            self._OAPI_STREAM_URL[int(self.p.practice)],
            port=443,
            ssl=True,
            token=self.p.token,
            datetime_format="UNIX",
        )

    def start(self, data=None, broker=None):
        # Datas require some processing to kickstart data reception
        if data is None and broker is None:
            self.cash = None
            return

        if data is not None:
            self._env = data._env
            # For datas simulate a queue with None to kickstart co
            self.datas.append(data)

            if self.broker is not None:
                self.broker.data_started(data)

        elif broker is not None:
            self.broker = broker
            self.streaming_events()
            self.broker_threads()

    def stop(self):
        # signal end of thread
        if self.broker is not None:
            self.q_ordercreate.put(None)
            self.q_orderclose.put(None)
            self.q_account.put(None)

    def put_notification(self, msg, *args, **kwargs):
        self.notifs.append((msg, args, kwargs))

    def get_notifications(self):
        '''Return the pending "store" notifications'''
        self.notifs.append(None)  # put a mark / threads could still append
        return [x for x in iter(self.notifs.popleft, None)]

    def get_positions(self):
        '''Returns the currently open positions'''
        try:
            response = self.oapi.position.list_open(self.p.account)
            poslist = response.get('positions', 200)
        except (Exception):
            return None

        return poslist

    def get_granularity(self, timeframe, compression):
        '''Returns the granularity useable for oanda'''
        return self._GRANULARITIES.get((timeframe, compression), None)

    def get_instrument(self, dataname):
        '''Returns details about the requested instrument'''
        try:
            response = self.oapi.account.instruments(self.p.account,
                                              instruments=dataname)
            insts = response.get('instruments', 200)
        except (Exception):
            return None

        return insts[0] or None

    def get_cash(self):
        '''Returns the available cash'''
        return self._cash

    def get_value(self):
        '''Returns the account balance'''
        return self._value

    def broker_threads(self):
        self.q_account = queue.Queue()
        self.q_account.put(True)  # force an immediate update
        t = threading.Thread(target=self._t_account)
        t.daemon = True
        t.start()

        self.q_ordercreate = queue.Queue()
        t = threading.Thread(target=self._t_order_create)
        t.daemon = True
        t.start()

        self.q_orderclose = queue.Queue()
        t = threading.Thread(target=self._t_order_cancel)
        t.daemon = True
        t.start()

        # Wait once for the values to be set
        self._evt_acct.wait(self.p.account_tmout)

    def streaming_events(self, tmout=None):
        '''Create threads for event streaming'''
        q = queue.Queue()
        kwargs = {'q': q, 'tmout': tmout}
        t = threading.Thread(target=self._t_streaming_events, kwargs=kwargs)
        t.daemon = True
        t.start()
        return q

    def streaming_prices(self, dataname, tmout=None):
        q = queue.Queue()
        kwargs = {'q': q, 'dataname': dataname, 'tmout': tmout}
        t = threading.Thread(target=self._t_streaming_prices, kwargs=kwargs)
        t.daemon = True
        t.start()
        return q

    def order_create(self, order, stopside=None, takeside=None, **kwargs):
        okwargs = dict()
        okwargs['instrument'] = order.data._dataname
        okwargs['units'] = abs(order.created.size)
        okwargs['side'] = 'buy' if order.isbuy() else 'sell'
        okwargs['type'] = self._ORDEREXECS[order.exectype]
        if order.exectype != bt.Order.Market:
            okwargs['price'] = order.created.price
            if order.valid is None:
                # 1 year and datetime.max fail ... 1 month works
                valid = datetime.utcnow() + timedelta(days=30)
            else:
                valid = order.data.num2date(order.valid)
                # To timestamp with seconds precision
            okwargs['expiry'] = int((valid - self._DTEPOCH).total_seconds())

        if order.exectype == bt.Order.StopLimit:
            okwargs['lowerBound'] = order.created.pricelimit
            okwargs['upperBound'] = order.created.pricelimit

        if order.exectype == bt.Order.StopTrail:
            okwargs['trailingStop'] = order.trailamount

        if stopside is not None:
            okwargs['stopLoss'] = stopside.price

        if takeside is not None:
            okwargs['takeProfit'] = takeside.price

        okwargs.update(**kwargs)  # anything from the user

        self.q_ordercreate.put((order.ref, okwargs,))
        return order

    def order_cancel(self, order):
        self.q_orderclose.put(order.ref)
        return order

    def candles(self, dataname, dtbegin, dtend, timeframe, compression,
                candleFormat, includeFirst):
        kwargs = locals().copy()
        kwargs.pop('self')
        kwargs['q'] = q = queue.Queue()
        t = threading.Thread(target=self._t_candles, kwargs=kwargs)
        t.daemon = True
        t.start()
        return q

    def _t_streaming_events(self, q, tmout=None):
        if tmout is not None:
            _time.sleep(tmout)

        try:
            response = self.oapi_stream.transaction.stream(self.p.account)
            for msg_type, msg in response.parts():
                if msg_type == "transaction.Transaction":
                    self._transaction(msg.dict())
        except Exception as e:
            q.put(e)

    def _t_streaming_prices(self, dataname, q, tmout):
        if tmout is not None:
            _time.sleep(tmout)

        try:
            response = self.oapi_stream.pricing.stream(
                self.p.account,
                instruments=dataname,
            )

            for msg_type, msg in response.parts():
                if msg_type == "pricing.Price":
                    q.put(msg.dict())
        except Exception as e:
            q.put(e)


    def _t_account(self):
        # Invoked from api thread, fetches account summary and sets current
        # values from oanda account
        while True:
            try:
                msg = self.q_account.get(timeout=self.p.account_tmout)
                if msg is None:
                    break  # end of thread
            except queue.Empty:  # tmout -> time to refresh
                pass

            try:
                response = self.oapi.account.summary(self.p.account)
                accinfo = response.get('account', 200)
            except Exception as e:
                self.put_notification(e)
                continue

            try:
                self._cash = accinfo.marginAvailable
                self._value = accinfo.balance
                self._currency = accinfo.currency
                self._marginRate = accinfo.marginRate
            except KeyError:
                pass

            self._evt_acct.set()

    def _t_candles(self, dataname, dtbegin, dtend, timeframe, compression,
                   candleFormat, includeFirst, q):

        granularity = self.get_granularity(timeframe, compression)
        if granularity is None:
            q.put(None)
            return

        dtkwargs = {}
        if dtbegin is not None:
            dtkwargs['from'] = int((dtbegin - self._DTEPOCH).total_seconds())
            dtkwargs['includeFirst'] = int(includeFirst)

        if dtend is not None:
            dtkwargs['to'] = int((dtend - self._DTEPOCH).total_seconds())

        try:
            response = self.oapi.instrument.candles(dataname,
                                             granularity=granularity,
                                             price=candleFormat,
                                             **dtkwargs)
        except Exception as e:
            return

        for candle in response.get('candles'):
            q.put(candle.dict())

        q.put({})  # end of transmission'''

    def _transaction(self, trans):
        # Invoked from Streaming Events. May actually receive an event for an
        # oid which has not yet been returned after creating an order. Hence
        # store if not yet seen, else forward to processor
        print(trans)
        # TODO
        ''' # Invoked from Streaming Events. May actually receive an event for an
        # oid which has not yet been returned after creating an order. Hence
        # store if not yet seen, else forward to processer
        ttype = trans['type']
        if ttype == 'MARKET_ORDER_CREATE':
            try:
                oid = trans['tradeReduced']['id']
            except KeyError:
                try:
                    oid = trans['tradeOpened']['id']
                except KeyError:
                    return  # cannot do anything else

        elif ttype in self._X_ORDER_CREATE:
            oid = trans['id']
        elif ttype == 'ORDER_FILLED':
            oid = trans['orderId']

        elif ttype == 'ORDER_CANCEL':
            oid = trans['orderId']

        elif ttype == 'TRADE_CLOSE':
            oid = trans['id']
            pid = trans['tradeId']
            if pid in self._orders and False:  # Know nothing about trade
                return  # can do nothing

            # Skip above - at the moment do nothing
            # Received directly from an event in the WebGUI for example which
            # closes an existing position related to order with id -> pid
            # COULD BE DONE: Generate a fake counter order to gracefully
            # close the existing position
            msg = ('Received TRADE_CLOSE for unknown order, possibly generated'
                   ' over a different client or GUI')
            self.put_notification(msg, trans)
            return

        else:  # Go aways gracefully
            try:
                oid = trans['id']
            except KeyError:
                oid = 'None'

            msg = 'Received {} with oid {}. Unknown situation'
            msg = msg.format(ttype, oid)
            self.put_notification(msg, trans)
            return

        try:
            oref = self._ordersrev[oid]
            self._process_transaction(oid, trans)
        except KeyError:  # not yet seen, keep as pending
            self._transpend[oid].append(trans)'''

    def _process_transaction(self, oid, trans):
        '''try:
            oref = self._ordersrev.pop(oid)
        except KeyError:
            return

        ttype = trans['type']

        if ttype in self._X_ORDER_FILLED:
            size = trans['units']
            if trans['side'] == 'sell':
                size = -size
            price = trans['price']
            self.broker._fill(oref, size, price, ttype=ttype)

        elif ttype in self._X_ORDER_CREATE:
            self.broker._accept(oref)
            self._ordersrev[oid] = oref

        elif ttype in 'ORDER_CANCEL':
            reason = trans['reason']
            if reason == 'ORDER_FILLED':
                pass  # individual execs have done the job
            elif reason == 'TIME_IN_FORCE_EXPIRED':
                self.broker._expire(oref)
            elif reason == 'CLIENT_REQUEST':
                self.broker._cancel(oref)
            else:  # default action ... if nothing else
                self.broker._reject(oref)'''

    def _t_order_create(self):
        '''while True:
            msg = self.q_ordercreate.get()
            if msg is None:
                break

            oref, okwargs = msg
            try:
                o = self.oapi.create_order(self.p.account, **okwargs)
            except Exception as e:
                self.put_notification(e)
                self.broker._reject(order.ref)
                return

            # Ids are delivered in different fields and all must be fetched to
            # match them (as executions) to the order generated here
            _o = {'id': None}
            oids = list()
            for oidfield in self._OIDSINGLE:
                if oidfield in o and 'id' in o[oidfield]:
                    oids.append(o[oidfield]['id'])

            for oidfield in self._OIDMULTIPLE:
                if oidfield in o:
                    for suboidfield in o[oidfield]:
                        oids.append(suboidfield['id'])

            if not oids:
                self.broker._reject(oref)
                return

            self._orders[oref] = oids[0]
            self.broker._submit(oref)
            if okwargs['type'] == 'market':
                self.broker._accept(oref)  # taken immediately

            for oid in oids:
                self._ordersrev[oid] = oref  # maps ids to backtrader order

                # An transaction may have happened and was stored
                tpending = self._transpend[oid]
                tpending.append(None)  # eom marker
                while True:
                    trans = tpending.popleft()
                    if trans is None:
                        break
                    self._process_transaction(oid, trans)
        '''
    def _t_order_cancel(self):
        while True:
            oref = self.q_orderclose.get()
            if oref is None:
                break

            oid = self._orders.get(oref, None)
            if oid is None:
                continue  # the order is no longer there
            try:
                o = self.oapi.trade.close(self.p.account, oid)
            except Exception as e:
                continue  # not cancelled - FIXME: notify

            self.broker._cancel(oref)
