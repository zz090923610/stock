#!/usr/bin/env python3
# noinspection PyCompatibility
from pathlib import Path

from stock.common.common_func import *
from stock.common.communction import simple_publish
from stock.common.file_operation import mkdirs
from stock.common.time_util import load_stock_date_list_from_tick_files, load_last_date
import tushare as ts
TODAY = load_last_date()




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
        if (d not in date_list_tick) & (d >= COMMON_VARS_OBJ.START_DATE):
            to_do_date_list.append('%s+%s' % (stock, d))
    return to_do_date_list


# noinspection PyBroadException
def _download_one_stock_one_day(scode_a_day):
    (stock, a_day) = scode_a_day.split('+')[0], scode_a_day.split('+')[1]
    if Path('%s/tick_data/%s/%s_%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock, stock, a_day)).is_file():
        return
    try:
        data = ts.get_tick_data(stock, date=a_day,src='tt')
    except:
        return
    try:
        if data.iloc[0]['time'].find("当天没有数据") == -1:
            data.to_csv('%s/tick_data/%s/%s_%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock, stock, a_day))
    except KeyboardInterrupt:
        exit(0)
    except:
        logging('ERROR Get Tick %s %s' % (stock, a_day))
    if not Path('%s/tick_data/%s/%s_%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock, stock, a_day)).is_file():
        logging('Tick Download failed for %s %s' % (stock, a_day), silence=True)
        simple_publish('tick_detail', '%s_%s_failed' % (stock, a_day))
    else:
        simple_publish('tick_detail','%s_%s_success' %(stock, a_day))


def download_tick():
    all_work_list = []
    print('Analysis Tick list')
    simple_publish('tick_update', 'analysis_start')
    for stock in BASIC_INFO.symbol_list:
        all_work_list += generate_day_list_for_stock(stock)
    simple_publish('tick_update', 'analysis_finished_%d' % len(all_work_list))
    simple_publish('tick_update', 'download_start')
    pool = mp.Pool(64)
    for stock in all_work_list:
        pool.apply_async(_download_one_stock_one_day, args=(stock,))
    pool.close()
    pool.join()
    simple_publish('tick_update', 'download_finished')

if __name__ == "__main__":
    download_tick()
