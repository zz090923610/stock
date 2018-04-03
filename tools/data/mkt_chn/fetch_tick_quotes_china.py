# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

# REGDIR( tick_quotes/china )

import itertools
import os
from multiprocessing import Pool

import tushare as ts

from tools.data.path_hdl import path_expand, directory_ensure, file_exist
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import logging
from tools.data.mkt_chn.symbol_list_china_hdl import SymbolListHDL

msg_source = 'TickQuoteUpdaterTushare'

calendar = MktCalendar()


class TickQuoteUpdaterTushare:
    """
    Fetch tick data for specified symbols and specified dates.
    Downloaded files should be saved to path $PROGRAM_DATA_ROOT/tick_quotes/china/%s/%s.csv % (symbol, date)
    $symbol/$date.csv: contains all tick data for of stock with symbol during date YYYY-MM-DD, with the header:
        [time,price,change,volume,amount,type]
    where:
        time:   filled time, HH:MM:SS
        price: filled price
        change: price - price_previous_row
        volume: traded shares / 100
        amount: volume * 100 * price
        type::  buy(on purpose)/sell(on purpose) or cannot_decide
    """

    # DEPENDENCY( tushare )
    def __init__(self):
        self.symbol_list_hdl = SymbolListHDL()
        self.dir = path_expand('tick_quotes/china')

    # noinspection PyMethodMayBeStatic
    def get_tick_one_stock_one_day(self, symbol, date, force):
        """
        fetch tick data for one symbol on specified date.
        :param symbol:  symbol of listed company
        :param date:    date you want, in format YYYY-NN-DD
        :param force:   rewrite existing files
        """
        if self.check_if_exist(symbol, date) and force is False:
            logging(msg_source, '%s/%s_exists' % (symbol, date))
            return
        df = ts.get_tick_data(symbol, date=date, src='tt')
        if df is None:
            logging(msg_source, '%s/%s_failed' % (symbol, date), method='all')
            return
        directory_ensure(os.path.join(self.dir, symbol))
        df.to_csv(os.path.join(self.dir, symbol, "%s.csv" % date), index=False)
        logging(msg_source, '%s/%s_success' % (symbol, date))

    def check_if_exist(self, symbol, date):
        return file_exist(os.path.join(self.dir, symbol, "%s.csv" % date))

    def get_tick_multiple(self, symbol_list, date_list, force=False):
        """
        get tick data given a symbol_list and a date_list
        :param symbol_list: [] of symbols
        :param date_list:   [] of YYYY-MM-DD
        :param force:   whether to rewrite existing file
        """
        force = [force]
        logging(msg_source, '%s/start_%d' % (msg_source, len(self.symbol_list_hdl.symbol_list)), method='all')
        pool = Pool(16)
        for params in itertools.product(symbol_list, date_list, force):
            pool.apply_async(self.get_tick_one_stock_one_day, args=params)
        pool.close()
        pool.join()
        logging(msg_source, '%s/finish' % msg_source, method='all')


# CMDEXPORT ( FETCH TICK {date_or_dates} ) update_tick_quotes
def update_tick_quotes(date_or_dates):
    """
    Export this function to Control Framework, a control command like:
        FETCH TICK 2017-01-28
    can be added to .ctrl batch file to save some work.
    :param date_or_dates: YYYY-MM-DD or [YYYY-MM-DD, ...]
    """
    dates = [date_or_dates] if type(date_or_dates) == str else date_or_dates
    dates = [calendar.parse_date(i) for i in dates]
    tick = TickQuoteUpdaterTushare()
    tick.get_tick_multiple(tick.symbol_list_hdl.symbol_list, dates)
