from tools.io import *
from multiprocessing import Pool
import tushare as ts

from tools.symbol_list_china_hdl import SymbolListHDL
from configs.path import DIRs

msg_source = 'day_level_quotes_china'

# TODO: implement backup sources, implement automatic source switch
# TODO: add windows support

class DayLevelQuoteUpdaterTushare:
    # DEPENDENCY( thshare )
    def __init__(self):
        self.symbol_list_hdl = SymbolListHDL()
        self.dir = DIRs.get('DAY_LEVEL_QUOTES_CHINA')

    # noinspection PyMethodMayBeStatic
    def get_data_one_stock(self, stock, start, end, store_dir):
        df = ts.get_hist_data(stock, start=start, end=end)
        if df is None:
            out(msg_source, '%s/%s_failed' % (msg_source, stock))
            return
        df = df.reindex(index=df.index[::-1])
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


if __name__ == '__main__':
    a = DayLevelQuoteUpdaterTushare()
    a.get_data_all_stock(start='2017-01-01', end='2017-12-20')
