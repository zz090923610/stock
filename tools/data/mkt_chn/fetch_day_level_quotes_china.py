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
        """
        Fetch day level quotes for one symbol.
        :param symbol:  Stock symbol, string of 6 digits.
        :param start:   We want data start from this date, string of "YYYY-MM-DD" format
        :param end:     We want data no later than this date. string of "YYYY-MM-DD" format
        :param store_dir: the DIRECTORY where our fetched data should be stored.
        :return: None if no exception happens else return symbol
        """
        df = ts.get_hist_data(symbol, start=start, end=end)
        if df is None:
            logging(msg_source, '[ ERROR ] DayLevelQuoteUpdaterTushare_%s failed' % symbol)
            return symbol
        df = df.reindex(index=df.index[::-1])
        symbol_str = self.symbol_dict.market_code_of_symbol(symbol)
        name = self.symbol_dict.name_dict.get(symbol)
        df['name'] = name
        df['symbol'] = symbol_str
        df.to_csv('%s/%s.csv' % (store_dir, symbol))
        logging(msg_source, '[ INFO ] DayLevelQuoteUpdaterTushare_%s_success' % symbol)
        return None

    def get_data_all_symbols(self, start, end):
        """
        Fetch day level quotes for all symbols.
        :param start:   We want data start from this date, string of "YYYY-MM-DD" format
        :param end:     We want data no later than this date. string of "YYYY-MM-DD" format
        """
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
        self.ts_api = ts.get_apis()
        self.symbol_list_hdl = SymbolListHDL()
        self.dir = path_expand('day_quotes/china')
        directory_ensure(self.dir)
        self.symbol_dict = SymbolListHDL()
        self.symbol_dict.load()

    def __del__(self):
        """
        Need to disconnect from TXD server first.
        """
        try:
            self.ts_api[0].disconnect()
            self.ts_api[1].disconnect()
        except Exception:
            pass

    def get_data_one_symbol(self, symbol, start, end, store_dir):
        self._get_data_one_symbol(symbol, start, end, store_dir)

    # noinspection PyMethodMayBeStatic
    def _get_data_one_symbol(self, symbol, start, end, store_dir):
        from tushare.util.formula import MA
        from tushare.stock import cons as ct
        df = ts.bar(symbol, self.ts_api, start_date=calendar.calc_t(start, '-', 20), end_date=end, adj='qfq',
                    ma=[5, 10, 20], factors=['tor'])

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
        symbol_str = self.symbol_dict.market_code_of_symbol(symbol)
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


# noinspection PyBroadException
class DayLevelQuoteUpdaterTushareNew:
    # DEPENDENCY( tushare )
    def __init__(self):
        self.symbol_list_hdl = SymbolListHDL()
        self.dir = path_expand('day_quotes/china')
        directory_ensure(self.dir)
        self.symbol_dict = SymbolListHDL()
        self.symbol_dict.load()

    # noinspection PyMethodMayBeStatic
    def get_data_one_symbol(self, symbol, start, end, store_dir):
        """
        Fetch day level quotes for one symbol.
        :param symbol:  Stock symbol, string of 6 digits.
        :param start:   We want data start from this date, string of "YYYY-MM-DD" format
        :param end:     We want data no later than this date. string of "YYYY-MM-DD" format
        :param store_dir: the DIRECTORY where our fetched data should be stored.
        :return: None if no exception happens else return symbol
        """
        df = ts.get_k_data(symbol, start=calendar.calc_t(start, '-', 20), end=end)
        df2 = ts.get_k_data(symbol)
        df = df.append(df2)
        if df is None:
            logging(msg_source, '[ ERROR ] DayLevelQuoteUpdaterTushare_%s failed' % symbol)
            return symbol
        df.sort_values(by='date', ascending=True, inplace=True)
        df.drop_duplicates(subset='date', inplace=True)
        symbol_str = self.symbol_dict.market_code_of_symbol(symbol)
        name = self.symbol_dict.name_dict.get(symbol)
        df['name'] = name
        df['symbol'] = symbol_str
        outstanding = int(float(self.symbol_dict.outstanding_dict[symbol]) * 1000000)
        df['turnover'] = df['volume'] / outstanding * 100
        df['outstanding'] = outstanding * 100
        df['prev_close_price'] = df['close'].shift(1)
        df['price_change'] = df['close'] - df['prev_close_price']
        df['p_change'] = df['price_change'] / df['prev_close_price']
        df['amount'] = ((df['high'] + df['low']) / 3 + (df['open'] + df['close']) / 6) * df['volume'] * 100
        df['ma5'] = df['close']
        df['ma10'] = df['close']
        df['ma20'] = df['close']

        df['v_ma5'] = df['volume']
        df['v_ma10'] = df['volume']
        df['v_ma20'] = df['volume']

        for loop in range(1, 20):
            df['prev_close_%d' % loop] = df['close'].shift(loop)
            df['ma5'] = df['ma5'] + df['prev_close_%d' % loop] if loop < 5 else df['ma5']
            df['ma10'] = df['ma10'] + df['prev_close_%d' % loop] if loop < 10 else df['ma10']
            df['ma20'] = df['ma20'] + df['prev_close_%d' % loop] if loop < 20 else df['ma20']

            df['prev_volume_%d' % loop] = df['volume'].shift(loop)
            df['v_ma5'] = df['v_ma5'] + df['prev_volume_%d' % loop] if loop < 5 else df['v_ma5']
            df['v_ma10'] = df['v_ma10'] + df['prev_volume_%d' % loop] if loop < 10 else df['v_ma10']
            df['v_ma20'] = df['v_ma20'] + df['prev_volume_%d' % loop] if loop < 20 else df['v_ma20']

        df['ma5'] /= 5
        df['ma10'] /= 10
        df['ma20'] /= 20

        df['v_ma5'] /= 5
        df['v_ma10'] /= 10
        df['v_ma20'] /= 20
        df = df.round(
            {'turnover': 5, 'price_change': 3, 'p_change': 5, 'ma5': 3, 'ma10': 3, 'ma20': 3, 'v_ma5': 1, 'v_ma10': 1,
             'v_ma20': 1, 'amount': 2})
        outcols = ['date', 'open', 'high', 'close', 'low', 'volume', 'amount', 'price_change', 'p_change', 'turnover',
                   'ma5',
                   'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20', 'name', 'symbol', 'outstanding']
        df = df[df['date'] >= start]
        df[outcols].to_csv('%s/%s.csv' % (store_dir, symbol), index=False)
        logging(msg_source, '[ INFO ] DayLevelQuoteUpdaterTushare_%s_success' % symbol)
        return None

    def get_data_all_symbols(self, start, end):
        """
        Fetch day level quotes for all symbols.
        :param start:   We want data start from this date, string of "YYYY-MM-DD" format
        :param end:     We want data no later than this date. string of "YYYY-MM-DD" format
        """
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
        logging(msg_source, '[ INFO ] finished_fetching', method='all')


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
    """
    Export this function to Control Framework, a control command like:
        FETCH OHCL 2017-01-01 2017-01-28
    can be added to .ctrl batch file to save some work.
        :param start_date:   We want data start from this date, string of "YYYY-MM-DD" format
        :param end_date:     We want data no later than this date. string of "YYYY-MM-DD" format
    """
    start_date = calendar.parse_date(start_date)
    end_date = calendar.parse_date(end_date)
    a = DayLevelQuoteUpdaterTushareNew()
    a.get_data_all_symbols(start=calendar.parse_date(start_date), end=calendar.parse_date(end_date))
