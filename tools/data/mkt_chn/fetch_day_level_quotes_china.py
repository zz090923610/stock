# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

from multiprocessing import Pool
from time import sleep

import tushare as ts

from tools.data.path_hdl import path_expand, directory_ensure
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import *
from tools.symbol_list_china_hdl import SymbolListHDL

msg_source = '[ DayLevelQuoteUpdater ]'

# TODO: implement backup sources, implement automatic source switch
# TODO: serious data missing when using ts.get_hist_data

# REGDIR( day_quotes/china )

calendar = MktCalendar()

# This module can fetch day level quotes(aka candlestick data) for all symbols from Chinese Stock Markets.
# Intended to implemented all 5 sources, each should work as backup of others if failed.

# all sources should implement:

#    def __init__(self):
#        pass
#    def __del__(self):
#        pass
#    def get_data_one_symbol(self, symbol, start, end, store_dir):
#        pass
#    def get_data_all_symbols(self, start, end):
#        pass

# DayLevelQuoteUpdaterTushare is faster since I can use multiprocessing, but with data missing.
# DayLevelQuoteUpdaterTushareTXD is much slower due to restriction but with high quality data.


class DayLevelQuoteUpdaterTushare:
    # DEPENDENCY( tushare )
    def __init__(self):
        self.symbol_list_hdl = SymbolListHDL()
        self.dir = path_expand('day_quotes/china')
        directory_ensure(self.dir)
        self.symbol_dict = SymbolListHDL()
        self.symbol_dict.load()

    # noinspection PyMethodMayBeStatic
    def get_data_one_symbol(self, symbol, start, end, store_dir):
        df = ts.get_hist_data(symbol, start=start, end=end)
        if df is None:
            out(msg_source, '[ ERROR ] % failed' % symbol)
            return symbol
        df = df.reindex(index=df.index[::-1])
        symbol_str = self.symbol_dict.market_symbol_of_stock(symbol)
        name = self.symbol_dict.name_dict.get(symbol)
        df['name'] = name
        df['symbol'] = symbol_str
        df.to_csv('%s/%s.csv' % (store_dir, symbol))
        out(msg_source, '[ INFO ] %s_success' % symbol)
        return None

    def get_data_all_symbols(self, start, end):
        print("DayLevelQuoteUpdaterTushare Fetching all symbols from %s to %s" % (start, end))
        out(msg_source, '[ INFO ] start_fetching_%d' % len(self.symbol_list_hdl.symbol_list))
        failed_list = []
        pool = Pool(16)
        for i in self.symbol_list_hdl.symbol_list:
            pool.apply_async(self.get_data_one_symbol, args=(i, start, end, self.dir), callback=failed_list.append)
        pool.close()
        pool.join()
        # Use backup source to fetch failed symbols.
        failed_list = [x for x in failed_list if x is not None]
        if len(failed_list):
            print('retry:', failed_list)
            a = DayLevelQuoteUpdaterTushareTXD()
            for i in failed_list:
                a.get_data_one_symbol(i, start, end, self.dir)
            a.__del__()
        out(msg_source, '[ INFO ] finished_fetching')
        print("DayLevelQuoteUpdaterTushare Fetching Finished")


class DayLevelQuoteUpdaterTushareTXD:
    # DEPENDENCY( tushare )
    def __init__(self):
        self.ts_api = None
        self.symbol_list_hdl = SymbolListHDL()
        self.dir = path_expand('day_quotes/china')
        directory_ensure(self.dir)
        self.symbol_dict = SymbolListHDL()
        self.symbol_dict.load()

    def __del__(self):
        if self.ts_api:
            self.ts_api[0].disconnect()
            self.ts_api[1].disconnect()

    # noinspection PyMethodMayBeStatic
    def get_data_one_symbol(self, symbol, start, end, store_dir):
        from tushare.util.formula import MA
        from tushare.stock import cons as ct
        if not self.ts_api:
            self.ts_api = ts.get_apis()
        # TODO by implementing calendar start-n validation, fill out right upper corner of df's MAs.
        # df = ts.bar(symbol, self.ts_api, start_date=start-20, end_date=end, adj='qfq', ma=[5, 10, 20],
        # factors=['tor'])
        df = None
        for _ in range(5):
            df = ts.bar(symbol, self.ts_api, start_date=start, end_date=end, adj='qfq', ma=[5, 10, 20], factors=['tor'])
            if df is not None:
                break
            sleep(1)
            print("retry:", symbol)
        if df is None:
            out(msg_source, '[ ERROR ] % failed' % symbol)
            return
        for x in [5, 10, 20]:
            df['v_ma%d' % x] = MA(df['vol'], x).map(ct.FORMAT).shift(-(x - 1))

        df['price_change'] = df['close'] - df['close'].shift(-1)
        df['p_change'] = df['price_change'] / df['close'].shift(-1) * 100

        df = df.rename(columns={'code': 'symbol', 'vol': 'volume', 'tor': 'turnover'})
        df.index.names = ['date']

        df = df.reindex(index=df.index[::-1])  # ???
        symbol_str = self.symbol_dict.market_symbol_of_stock(symbol)
        name = self.symbol_dict.name_dict.get(symbol)
        df['name'] = name
        df['symbol'] = symbol_str
        column_order = ['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5', 'ma10',
                        'ma20',
                        'v_ma5', 'v_ma10', 'v_ma20', 'turnover', 'name', 'symbol']
        df[column_order].to_csv('%s/%s.csv' % (store_dir, symbol), float_format='%.2f')
        out(msg_source, '[ INFO ] %s_success' % symbol)

    def get_data_all_symbols(self, start, end):
        print("DayLevelQuoteUpdaterTushareTXD Fetching all symbols from %s to %s" % (start, end))
        if not self.ts_api:
            self.ts_api = ts.get_apis()
        out(msg_source, '[ INFO ] start_fetching_%d' % len(self.symbol_list_hdl.symbol_list))
        for i in self.symbol_list_hdl.symbol_list:
            self.get_data_one_symbol(i, start, end, self.dir)
        out(msg_source, '[ INFO ] finished_fetching')
        print("DayLevelQuoteUpdaterTushareTXD Fetching Finished")
        self.__del__()


class DayLevelQuoteUpdaterSinaLevel1:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def get_data_one_symbol(self, symbol, start, end, store_dir):
        pass

    def get_data_all_symbols(self, start, end):
        pass


class DayLevelQuoteUpdaterSinaLevel2:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def get_data_one_symbol(self, symbol, start, end, store_dir):
        pass

    def get_data_all_symbols(self, start, end):
        pass


class DayLevelQuoteUpdaterGTJA:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def get_data_one_symbol(self, symbol, start, end, store_dir):
        pass

    def get_data_all_symbols(self, start, end):
        pass


# CMDEXPORT ( FETCH OHCL {} {} ) update_day_level_quotes
def update_day_level_quotes(start_date, end_date):
    a = DayLevelQuoteUpdaterTushareTXD()
    a.get_data_all_symbols(start=calendar.validate_date(start_date), end=calendar.validate_date(end_date))
