#!/usr/bin/env python3
import multiprocessing
# noinspection PyCompatibility
from pathlib import Path

import progressbar

from stock.common.common_func import *

bar = progressbar.ProgressBar(max_value=len(BASIC_INFO.symbol_list), redirect_stdout=True)
bar_cnt_lock = multiprocessing.Lock()
bar_cnt_path = '/tmp/stock_tick_bar_cnt.pickle'
TODAY = get_today()


# noinspection PyShadowingNames
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


# noinspection PyShadowingNames
def generate_day_list_for_stock(stock):
    try:
        date_list_tick = load_stock_date_list_from_tick_files(stock)
    except FileNotFoundError:
        mkdirs(BASIC_INFO.symbol_list)
        date_list_tick = load_stock_date_list_from_tick_files(stock)
    date_list_daily = load_stock_date_list_from_daily_data(stock)
    to_do_date_list = []
    for d in date_list_daily:
        if (d not in date_list_tick) & (d >= START_DATE):
            to_do_date_list.append('%s+%s' % (stock, d))
    adding_bar_cnt(bar_cnt_path)
    return to_do_date_list


# noinspection PyBroadException
def _download_one_stock_one_day(scode_a_day):
    (scode, a_day) = scode_a_day.split('+')[0], scode_a_day.split('+')[1]
    if Path('%s/tick_data/%s/%s_%s.csv' % (stock_data_root, scode, scode, a_day)).is_file():
        return
    try:
        data = ts.get_tick_data(scode, date=a_day)
    except:
        return
    try:
        if data.iloc[0]['time'].find("当天没有数据") == -1:
            data.to_csv('%s/tick_data/%s/%s_%s.csv' % (stock_data_root, scode, scode, a_day))
            adding_bar_cnt(bar_cnt_path)
    except KeyboardInterrupt:
        exit(0)
    except:
        logging('ERROR Get Tick %s %s' % (scode, a_day))
        adding_bar_cnt(bar_cnt_path)
    if not Path('%s/tick_data/%s/%s_%s.csv' % (stock_data_root, scode, scode, a_day)).is_file():
        logging('Tick Download failed for %s %s' % (scode, a_day), silence=True)


if __name__ == "__main__":
    subprocess.call('rm %s 2>/dev/null' % bar_cnt_path, shell=True)
    with open(bar_cnt_path, 'wb') as f:
        pickle.dump({'cnt': 0}, f)
    all_work_list = []
    print('Analysis Tick list')
    for stock in BASIC_INFO.symbol_list:
        all_work_list += generate_day_list_for_stock(stock)
    subprocess.call('rm %s 2>/dev/null' % bar_cnt_path, shell=True)
    bar.max_value = len(all_work_list)
    with open(bar_cnt_path, 'wb') as f:
        pickle.dump({'cnt': 0}, f)

    pool = mp.Pool(64)
    for stock in all_work_list:
        pool.apply_async(_download_one_stock_one_day, args=(stock,))
    pool.close()
    pool.join()
