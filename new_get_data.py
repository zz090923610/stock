#!/usr/bin/env python3
import multiprocessing
from multiprocessing import Pool
from common_func import *
from data_rt_sina import get_rt_data_dict, get_pd_from_rt_data_dict_of_stock
import progressbar

bar = progressbar.ProgressBar(max_value=len(BASIC_INFO.symbol_list), redirect_stdout=True)
bar_cnt_lock = multiprocessing.Lock()
TODAY = get_today()
RT_DICT = get_rt_data_dict()  # FIXME global update


def adding_bar_cnt(bar_cnt_path):
    bar_cnt_lock.acquire()
    # noinspection PyBroadException
    try:
        with open(bar_cnt_path, 'rb') as f:

            cnt = int(pickle.load(f)['cnt'])
    except:
        cnt = 0
    cnt += 1
    with open(bar_cnt_path, 'wb') as f:
        pickle.dump({'cnt': cnt}, f)
    bar.update(cnt)
    bar_cnt_lock.release()


def get_all_data_for_one_stock(stock):
    start = max(BASIC_INFO.time_to_market_dict[stock], START_DATE)
    df = ts.get_k_data(stock, autype='qfq', start=start, end=TODAY)
    if df is None:
        raise EOFError
    if TODAY not in df.date.tolist():
        rt_today = get_pd_from_rt_data_dict_of_stock(RT_DICT, stock)
        if rt_today is not None:
            if int(rt_today['volume'][0]) > 0:
                df = df.append(rt_today, ignore_index=True)
    df = df.drop_duplicates('date', keep='last')
    df = df.sort_values(by='date', ascending=True)
    df = df.reset_index()
    df = df.round({'open': 3, 'high': 3, 'close': 3, 'low': 3})
    df.volume = df.volume.astype(int)
    cols = ['date', 'open', 'high', 'close', 'low', 'volume']
    df[cols].to_csv('../stock_data/data/%s.csv' % stock, index=False)
    adding_bar_cnt('/tmp/stock_daily_bar_cnt.pickle')
    return stock


def get_all_data_for_all_stock(get_type='all'):
    subprocess.call('rm /tmp/stock_daily_bar_cnt.pickle 2>/dev/null', shell=True)
    with open('/tmp/stock_daily_bar_cnt.pickle', 'wb') as f:
        pickle.dump({'cnt': 0}, f)
    subprocess.call('mkdir -p ../stock_data/data', shell=True)
    finished_stock_list = []
    pool = mp.Pool(16)
    if get_type == 'all':
        print("Getting Daily Data")
        for i in BASIC_INFO.symbol_list:
            pool.apply_async(get_all_data_for_one_stock, args=(i,), callback=finished_stock_list.append)
    else:
        print("Updating Daily Data %s" % TODAY)
        for i in BASIC_INFO.symbol_list:
            pool.apply_async(get_update_for_one_stock, args=(i,), callback=finished_stock_list.append)
    pool.close()
    pool.join()
    subprocess.call('rm /tmp/stock_daily_bar_cnt.pickle 2>/dev/null', shell=True)


def get_update_for_one_stock(stock):
    try:
        df = pd.read_csv('../stock_data/data/%s.csv' % stock)
    except FileNotFoundError:
        get_all_data_for_one_stock(stock)
        return
    if TODAY in df.date.tolist():
        adding_bar_cnt('/tmp/stock_daily_bar_cnt.pickle')
        return
    rt_today = get_pd_from_rt_data_dict_of_stock(RT_DICT, stock)
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
    df[cols].to_csv('../stock_data/data/%s.csv' % stock, index=False)
    adding_bar_cnt('/tmp/stock_daily_bar_cnt.pickle')


if __name__ == "__main__":
    fetch_type = 'update'
    if len(sys.argv) == 0:
        get_all_data_for_all_stock(get_type=fetch_type)
    for loop in range(1, len(sys.argv)):
        if sys.argv[loop] == '--all':
            fetch_type = 'all'
        elif sys.argv[loop] == '--update':
            fetch_type = 'update'
    get_all_data_for_all_stock(get_type=fetch_type)
