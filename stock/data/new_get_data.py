#!/usr/bin/env python3
import multiprocessing
from multiprocessing import Pool
from stock.common.common_func import *
from stock.data.data_rt_sina import get_rt_data_dict, get_pd_from_rt_data_dict_of_stock
import progressbar

TODAY = load_last_date()


class DailyDataFetcher:
    def __init__(self, fetch_type='all', show_bar=False):
        self.RT_DICT = {}
        self.fetch_type = fetch_type
        self.show_bar = show_bar
        if self.show_bar:
            self.bar = progressbar.ProgressBar(max_value=len(BASIC_INFO.symbol_list), redirect_stdout=True)
            self.bar_cnt_lock = multiprocessing.Lock()

    def adding_bar_cnt(self, bar_cnt_path):
        self.bar_cnt_lock.acquire()
        # noinspection PyBroadException
        try:
            with open(bar_cnt_path, 'rb') as f:

                cnt = int(pickle.load(f)['cnt'])
        except:
            cnt = 0
        cnt += 1
        with open(bar_cnt_path, 'wb') as f:
            pickle.dump({'cnt': cnt}, f)
        self.bar.update(cnt)
        self.bar_cnt_lock.release()

    def _get_all_data_for_one_stock(self, stock):
        start = max(BASIC_INFO.time_to_market_dict[stock], COMMON_VARS_OBJ.START_DATE)
        df = ts.get_k_data(stock, autype='qfq', start=start, end=TODAY)
        if df is None:
            raise EOFError
        if TODAY not in df.date.tolist():
            rt_today = get_pd_from_rt_data_dict_of_stock(self.RT_DICT, stock)
            if rt_today is not None:
                if int(rt_today['volume'][0]) > 0:
                    df = df.append(rt_today, ignore_index=True)
        df = df.drop_duplicates('date', keep='last')
        df = df.sort_values(by='date', ascending=True)
        df = df.reset_index()
        df = df.round({'open': 3, 'high': 3, 'close': 3, 'low': 3})
        df.volume = df.volume.astype(int)
        cols = ['date', 'open', 'high', 'close', 'low', 'volume']
        df[cols].to_csv('%s/data/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock), index=False)
        if self.show_bar:
            self.adding_bar_cnt('/tmp/stock_daily_bar_cnt.pickle')
        simple_publish('daily_data_update', '%s_all' % stock)
        return stock

    def get_all_data_for_all_stock(self):
        simple_publish('daily_data_update', 'start_%s' % self.fetch_type)
        self.RT_DICT = get_rt_data_dict()
        if self.show_bar:
            subprocess.call('rm /tmp/stock_daily_bar_cnt.pickle 2>/dev/null', shell=True)
            with open('/tmp/stock_daily_bar_cnt.pickle', 'wb') as f:
                pickle.dump({'cnt': 0}, f)
            subprocess.call('mkdir -p %s/data' % COMMON_VARS_OBJ.stock_data_root, shell=True)
        finished_stock_list = []
        pool = mp.Pool(16)
        if self.fetch_type == 'all':
            print("Getting Daily Data")
            for i in BASIC_INFO.symbol_list:
                pool.apply_async(self._get_all_data_for_one_stock, args=(i,), callback=finished_stock_list.append)
        else:
            print("Updating Daily Data %s" % TODAY)
            for i in BASIC_INFO.symbol_list:
                pool.apply_async(self._get_update_for_one_stock, args=(i,), callback=finished_stock_list.append)
        pool.close()
        pool.join()
        subprocess.call('rm /tmp/stock_daily_bar_cnt.pickle 2>/dev/null', shell=True)
        simple_publish('daily_data_update', 'finished_%s' % self.fetch_type)

    def _get_update_for_one_stock(self, stock):
        try:
            df = pd.read_csv('%s/data/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock))
        except FileNotFoundError:
            self._get_all_data_for_one_stock(stock)
            return
        if TODAY in df.date.tolist():
            if self.show_bar:
                self.adding_bar_cnt('/tmp/stock_daily_bar_cnt.pickle')
            return
        rt_today = get_pd_from_rt_data_dict_of_stock(self.RT_DICT, stock)
        if rt_today is not None:
            if rt_today is not None:
                if int(rt_today['volume'][0]) > 0:
                    df = df.append(rt_today, ignore_index=True)
        df = df.sort_values(by='date', ascending=True)
        df = df.reset_index()
        cols = ['date', 'open', 'high', 'close', 'low', 'volume']
        df = df.drop_duplicates('date', keep='last')
        df = df.round({'open': 3, 'high': 3, 'close': 3, 'low': 3})
        df.volume = df.volume.astype(int)
        df[cols].to_csv('%s/data/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock), index=False)
        if self.show_bar:
            self.adding_bar_cnt('/tmp/stock_daily_bar_cnt.pickle')
        simple_publish('daily_data_update', '%s_update' % stock)


def get_daily_data_signal_daemon_callable():
    b = DailyDataFetcher(fetch_type='update', show_bar=False)
    b.get_all_data_for_all_stock()


if __name__ == "__main__":
    fetch_type = 'update'
    if len(sys.argv) == 0:
        a = DailyDataFetcher(fetch_type=fetch_type, show_bar=True)
        a.get_all_data_for_all_stock()
    for loop in range(1, len(sys.argv)):
        if sys.argv[loop] == '--all':
            fetch_type = 'all'
        elif sys.argv[loop] == '--update':
            fetch_type = 'update'
        a = DailyDataFetcher(fetch_type=fetch_type, show_bar=True)
        a.get_all_data_for_all_stock()
