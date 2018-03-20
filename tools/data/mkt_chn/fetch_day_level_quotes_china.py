# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

from multiprocessing import Pool
from time import sleep

import tushare as ts

from tools.data.path_hdl import path_expand, directory_ensure
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import *
from tools.data.mkt_chn.symbol_list_china_hdl import SymbolListHDL

msg_source = 'DayLevelQuoteUpdater'

# need to implement backup sources when necessary, implement automatic source switch

# REGDIR( day_quotes/china )

calendar = MktCalendar()


# This module can fetch day level quotes(aka candlestick data) for all symbols from Chinese Stock Markets.
# Intended to implemented all 5 sources, each should work as backup of others if failed.

# class for every source should implement:

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
    """
    Fetch day level data of list of symbols given a date range.
    Downloaded files should be saved to $PROGRAM_DATA_ROOT/day_quotes/china/%s.csv % symbol
    $symbol.csv: contains day level data with header:
        [date,open,high,close,low,volume,price_change,p_change,ma5,ma10,ma20,v_ma5,v_ma10,v_ma20,turnover,name,symbol]
    where:
        date:  date in format YYYY-MM-DD
        open:  stock price at 09:30AM YYYY-MM-DD
        high:   highest price among all prices of YYYY-MM-DD
        close:  stock price at 15:00PM YYYY-MM-DD
        low:    lowest price among all prices of YYYY-MM-DD
        volume: traded shares / 100
        price_change: close - prev_close
        p_change:   (close - prev_close) / prev_close * 100
        ma5:    moving average of price, with window size = 5
        ma10:    moving average of price, with window size = 10
        ma20:    moving average of price, with window size = 20
        v_ma5:  moving average of volume, with window size = 5
        v_ma10:  moving average of volume, with window size = 10
        v_ma20:  moving average of volume, with window size = 20
        turnover:   volume / outstanding shares * 100
        name:   short company name
        symbol: company symbol
    """

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
            logging(msg_source, '[ ERROR ] DayLevelQuoteUpdaterTushare_%s failed' % symbol)
            return symbol
        df = df.reindex(index=df.index[::-1])
        symbol_str = self.symbol_dict.market_code_of_stock(symbol)
        name = self.symbol_dict.name_dict.get(symbol)
        df['name'] = name
        df['symbol'] = symbol_str
        df.to_csv('%s/%s.csv' % (store_dir, symbol))
        logging(msg_source, '[ INFO ] DayLevelQuoteUpdaterTushare_%s_success' % symbol)
        return None

    def get_data_all_symbols(self, start, end):
        logging(msg_source, '[ INFO ] start_fetching_%d' % len(self.symbol_list_hdl.symbol_list), method='all')
        failed_list = []
        pool = Pool(16)
        for i in self.symbol_list_hdl.symbol_list:
            pool.apply_async(self.get_data_one_symbol, args=(i, start, end, self.dir), callback=failed_list.append)
        pool.close()
        pool.join()
        # Use backup source to fetch failed symbols.
        failed_list = [x for x in failed_list if x is not None]
        logging(msg_source, "[ INFO ] %d_symbols_update_failed" % len(failed_list), method='all')
        print(failed_list)
        # FIXME: TXD source as backup is way too unstable.
        # if len(failed_list):
        #    logging(msg_source, "[ INFO ] retry_%d_failed_symbols" % len(failed_list), method='all')
        #    print(failed_list)
        #    a = DayLevelQuoteUpdaterTushareTXD()
        #    for i in failed_list:
        #        a.get_data_one_symbol(i, start, end, self.dir)
        #    a.__del__()
        logging(msg_source, '[ INFO ] finished_fetching', method='all')


# noinspection PyBroadException
class DayLevelQuoteUpdaterTushareTXD:
    # DEPENDENCY( tushare )
    """
    Same input/output format as DayLevelQuoteUpdaterTushare
    """

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

    def get_data_one_symbol(self, symbol, start, end, store_dir):
        retry_cnt = 0
        while retry_cnt < 5:
            if retry_cnt > 0:
                try:
                    self.__del__()
                except Exception:
                    pass
            try:
                self.__del__()
                self._get_data_one_symbol(symbol, start, end, store_dir)
                break
            except OSError:
                retry_cnt += 1

    # noinspection PyMethodMayBeStatic
    def _get_data_one_symbol(self, symbol, start, end, store_dir):
        from tushare.util.formula import MA
        from tushare.stock import cons as ct
        if not self.ts_api:
            self.ts_api = ts.get_apis()
        df = None
        for _ in range(5):
            df = ts.bar(symbol, self.ts_api, start_date=calendar.calc_t(start, '-', 20), end_date=end, adj='qfq',
                        ma=[5, 10, 20], factors=['tor'])
            if df is not None:
                break
            sleep(1)
        if df is None:
            logging(msg_source, '[ ERROR ] DayLevelQuoteUpdaterTushareTXD_%s_failed' % symbol)
            return
        for x in [5, 10, 20]:
            df['v_ma%d' % x] = MA(df['vol'], x).map(ct.FORMAT).shift(-(x - 1))

        df['price_change'] = df['close'] - df['close'].shift(-1)
        df['p_change'] = df['price_change'] / df['close'].shift(-1) * 100

        df = df.rename(columns={'code': 'symbol', 'vol': 'volume', 'tor': 'turnover'})
        df.index.names = ['date']

        df = df.reindex(index=df.index[::-1])  # reverse rows
        symbol_str = self.symbol_dict.market_code_of_stock(symbol)
        name = self.symbol_dict.name_dict.get(symbol)
        df['name'] = name
        df['symbol'] = symbol_str
        column_order = ['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5', 'ma10',
                        'ma20',
                        'v_ma5', 'v_ma10', 'v_ma20', 'turnover', 'name', 'symbol']
        df = df[df.index >= start]
        df[column_order].to_csv('%s/%s.csv' % (store_dir, symbol), float_format='%.2f')
        logging(msg_source, '[ INFO ] DayLevelQuoteUpdaterTushareTXD_%s_success' % symbol)

    def get_data_all_symbols(self, start, end):
        if not self.ts_api:
            self.ts_api = ts.get_apis()
        logging(msg_source, '[ INFO ] start_fetching_%d' % len(self.symbol_list_hdl.symbol_list), method='all')
        for i in self.symbol_list_hdl.symbol_list:
            self.get_data_one_symbol(i, start, end, self.dir)
        logging(msg_source, '[ INFO ] finished_fetching', method='all')
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


# CMDEXPORT ( FETCH OHCL {start_date} {end_date} ) update_day_level_quotes
def update_day_level_quotes(start_date, end_date):
    start_date = calendar.parse_date(start_date)
    end_date = calendar.parse_date(end_date)
    a = DayLevelQuoteUpdaterTushare()
    a.get_data_all_symbols(start=calendar.parse_date(start_date), end=calendar.parse_date(end_date))
