import os

import itertools
import tushare as ts

from configs.path import DIRs
from tools.io import out
from tools.symbol_list_china_hdl import SymbolListHDL
from multiprocessing import Pool

msg_source = 'tick_quotes_china'


class TickQuoteUpdaterTushare:
    # DEPENDENCY( tushare )
    def __init__(self):
        self.symbol_list_hdl = SymbolListHDL()
        self.dir = DIRs.get('TICK_QUOTES_CHINA')

    # noinspection PyMethodMayBeStatic
    def get_tick_one_stock_one_day(self, stock, day, force):
        if self.check_if_exist(stock, day) and force is False:
            out(msg_source, '%s/%s/%s_exists' % (msg_source, stock, day))
            return
        df = ts.get_tick_data(stock, date=day, src='tt')
        if df is None:
            out(msg_source, '%s/%s_failed' % (msg_source, stock))
            return
        df = df.reindex(index=df.index[::-1])
        if not os.path.exists('%s/%s' % (self.dir, stock)):
            os.makedirs('%s/%s' % (self.dir, stock))
        df.to_csv('%s/%s/%s.csv' % (self.dir, stock, day))
        out(msg_source, '%s/%s/%s_success' % (msg_source, stock, day))

    def check_if_exist(self, stock, date):
        if os.path.exists(os.path.join(self.dir, stock, "%s.csv" % date)):
            return True
        else:
            return False

    def get_tick_multiple(self, stock_list, date_list, force=False):
        force = [force]
        out(msg_source, '%s/start_%d' % (msg_source, len(self.symbol_list_hdl.symbol_list)))
        pool = Pool(16)
        for params in itertools.product(stock_list, date_list, force):
            pool.apply_async(self.get_tick_one_stock_one_day, args=params)
        pool.close()
        pool.join()
        out(msg_source, '%s/finish' % msg_source)
