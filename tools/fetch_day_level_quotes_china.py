# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

from multiprocessing import Pool

import tushare as ts

from tools.data.path_hdl import path_expand, directory_ensure
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import *
from tools.symbol_list_china_hdl import SymbolListHDL

msg_source = 'day_level_quotes_china'

# TODO: implement backup sources, implement automatic source switch

# DIRREG( day_quotes/china )

calendar = MktCalendar()


class DayLevelQuoteUpdaterTushare:
    # DEPENDENCY( tushare )
    def __init__(self):
        self.symbol_list_hdl = SymbolListHDL()
        self.dir = path_expand('day_quotes/china')
        directory_ensure(self.dir)
        self.symbol_dict = SymbolListHDL()
        self.symbol_dict.load()

    # noinspection PyMethodMayBeStatic
    def get_data_one_stock(self, stock, start, end, store_dir):
        df = ts.get_hist_data(stock, start=start, end=end)
        if df is None:
            out(msg_source, '%s/%s_failed' % (msg_source, stock))
            return
        df = df.reindex(index=df.index[::-1])
        symbol_str = self.symbol_dict.market_symbol_of_stock(stock)
        name = self.symbol_dict.name_dict.get(stock)
        df['name'] = name
        df['symbol'] = symbol_str
        df.to_csv('%s/%s.csv' % (store_dir, stock))
        out(msg_source, '%s/%s_success' % (msg_source, stock))

    def get_data_all_stock(self, start, end):
        out(msg_source, '%s/start_%d' % (msg_source, len(self.symbol_list_hdl.symbol_list)))
        pool = Pool(16)
        for i in self.symbol_list_hdl.symbol_list:
            pool.apply_async(self.get_data_one_stock, args=(i, start, end, self.dir))
        pool.close()
        pool.join()
        out(msg_source, '%s/finish' % msg_source)


class DayLevelQuoteUpdaterSinaLevel1:
    pass


class DayLevelQuoteUpdaterSinaLevel2:
    pass


class DayLevelQuoteUpdaterGTJA:
    pass


# CMDEXPORT ( FETCH OHCL {} {} ) update_day_level_quotes
def update_day_level_quotes(start_date, end_date):
    a = DayLevelQuoteUpdaterTushare()
    a.get_data_all_stock(start=calendar.validate_date(start_date), end=calendar.validate_date(end_date))
