# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

# DIRREG( tick_quotes/china )

import itertools
import os
from multiprocessing import Pool

import tushare as ts

from tools.data.path_hdl import path_expand, directory_ensure, file_exist
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import out
from tools.symbol_list_china_hdl import SymbolListHDL

msg_source = 'tick_quotes_china'

calendar = MktCalendar()


class TickQuoteUpdaterTushare:
    # DEPENDENCY( tushare )
    def __init__(self):
        self.symbol_list_hdl = SymbolListHDL()
        self.dir = path_expand('tick_quotes/china')

    # noinspection PyMethodMayBeStatic
    def get_tick_one_stock_one_day(self, stock, date, force):
        if self.check_if_exist(stock, date) and force is False:
            out(msg_source, '%s/%s/%s_exists' % (msg_source, stock, date))
            return
        df = ts.get_tick_data(stock, date=date, src='tt')
        if df is None:
            out(msg_source, '%s/%s/%s_failed' % (msg_source, stock, date))
            return
        df = df.reindex(index=df.index[::-1])
        directory_ensure(os.path.join(self.dir, stock))
        df.to_csv(os.path.join(self.dir, stock, "%s.csv" % date))
        out(msg_source, '%s/%s/%s_success' % (msg_source, stock, date))

    def check_if_exist(self, stock, date):
        return file_exist(os.path.join(self.dir, stock, "%s.csv" % date))

    def get_tick_multiple(self, stock_list, date_list, force=False):
        force = [force]
        out(msg_source, '%s/start_%d' % (msg_source, len(self.symbol_list_hdl.symbol_list)))
        pool = Pool(16)
        for params in itertools.product(stock_list, date_list, force):
            pool.apply_async(self.get_tick_one_stock_one_day, args=params)
        pool.close()
        pool.join()
        out(msg_source, '%s/finish' % msg_source)


# CMDEXPORT ( FETCH TICK {date_or_dates} ) update_tick_quotes
def update_tick_quotes(date_or_dates):
    dates = [date_or_dates] if type(date_or_dates) == str else date_or_dates
    dates = [calendar.validate_date(i) for i in dates]
    tick = TickQuoteUpdaterTushare()
    tick.get_tick_multiple(tick.symbol_list_hdl.symbol_list, dates)
