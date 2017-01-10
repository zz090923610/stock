#!/usr/bin/env python3
import os
import sys
from multiprocessing.pool import Pool
from pathlib import Path
from common_func import *


def load_fail_to_repair_list(stock):
    try:
        with open('../stock_data/failed_downloaded_tick/%s.pickle' % stock, 'rb') as f:
            return pickle.load(f)
    except:
        return []


def download_stock(s_code):
    finished = False
    while not finished:
        current_file_date = get_last_date(s_code)
        start = max(IPO_DATE_LIST[s_code], '2008-01-01')

        if current_file_date is not None:
            start = current_file_date
        date_list = get_date_list(start, get_today(), timedelta(days=1))
        try:
            for a_day in date_list:
                _download_one_stock_one_day(s_code, a_day)
            finished = True
        except KeyboardInterrupt:
            exit(0)
        except:
            finished = False


def generate_day_list_for_stock(s_code):
    failed_loaded_list = load_fail_to_repair_list(s_code)
    current_file_date = get_last_date(s_code)
    start = max(IPO_DATE_LIST[s_code], '2008-01-01')
    all_date_list = get_stock_open_date_list(start)
    if current_file_date is None:
        return all_date_list
    date_list = []
    for day in all_date_list:
        if day in failed_loaded_list:
            continue
        if day >= current_file_date:
            date_list.append(day)
    return date_list


def generate_work_list(s_code, date_list):
    result = []
    for day in date_list:
        result.append('%s+%s' % (s_code, day))
    return result


def _download_one_stock_one_day(scode_a_day):
    (scode, a_day) = scode_a_day.split('+')[0], scode_a_day.split('+')[1]
    if Path('../stock_data/tick_data/%s/%s_%s.csv' % (scode, scode, a_day)).is_file():
        print('Exist %s %s' % (scode, a_day), file=sys.stderr)
        return
    print("Get %s %s" % (scode, a_day))
    data = ts.get_tick_data(scode, date=a_day)
    try:
        if data.iloc[0]['time'].find("当天没有数据") == -1:
            data.to_csv('../stock_data/tick_data/%s/%s_%s.csv' % (scode, scode, a_day))
    except KeyboardInterrupt:
        exit(0)
    except:
        print('ERROR Get %s %s' % (scode, a_day), file=sys.stderr)


def get_last_date(s_code):
    file_list = os.listdir('../stock_data/tick_data/%s' % s_code)
    if len(file_list) == 0:
        return None
    date_list = []
    for f in file_list:
        day = f.split('_')[1].split('.')[0]
        (y, m, d) = int(day.split('-')[0]), int(day.split('-')[1]), int(day.split('-')[2])
        date_list.append(datetime.datetime(y, m, d))
    return max(date_list).strftime("%Y-%m-%d")


if __name__ == "__main__":
    all_work_list = []
    for stock in SYMBOL_LIST:
        date_list = generate_day_list_for_stock(stock)
        all_work_list += generate_work_list(stock, date_list)

    p = Pool(POOL_SIZE)
    rs = p.imap_unordered(_download_one_stock_one_day, all_work_list)
    p.close()  # No more work
    list_len = len(all_work_list)
    while True:
        completed = rs._index
        if completed == list_len:
            break
        sys.stdout.write('Getting %.3f\n' % (completed / list_len))
        sys.stdout.flush()
        time.sleep(2)
    sys.stdout.write('Getting 1.000\n')
    sys.stdout.flush()
