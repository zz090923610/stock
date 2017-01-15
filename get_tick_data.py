#!/usr/bin/env python3
import os
import sys
from math import floor
from multiprocessing.pool import Pool
from pathlib import Path
from common_func import *
from qa_tick_lms import calculate_lms_for_stock_one_day, load_tick_data
import pandas as pd


def load_fail_to_repair_list(stock):
    try:
        with open('../stock_data/failed_downloaded_tick/%s.pickle' % stock, 'rb') as f:
            return pickle.load(f)
    except:
        return []


def load_something_for_stock_one_day(stock, day, something):
    volume = 0
    with open('../stock_data/data/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['date'] == day:
                volume = float(row[something])
    return volume


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
                _download_one_stock_one_day("%s+%s" % (s_code, a_day))
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
    try:
        data = ts.get_tick_data(scode, date=a_day)
    except:
        return
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


def align_tick_data_stock(stock):
    daily_date_list = load_stock_date_list_from_daily_data(stock)
    tick_date_list = load_stock_date_list_from_tick_files(stock)
    for (idx, day) in enumerate(daily_date_list):
        if day not in tick_date_list:
            if idx > 0:

                _download_one_stock_one_day('%s+%s' % (stock, day))
                if os.path.isfile('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, day)):
                    continue
                print('Still missing tick data for %s %s' % (stock, day))
                (buy_large, sell_large, buy_mid, sell_mid, buy_small, sell_small,
                 undirected_trade) = calculate_lms_for_stock_one_day(stock, daily_date_list[idx - 1])
                yesterday_volume = buy_large + sell_large + buy_mid + sell_mid + buy_small + sell_small + undirected_trade
                today_volume = load_something_for_stock_one_day(stock, day, 'volume')
                today_price = load_something_for_stock_one_day(stock, day, 'close')
                yesterday_tick = load_tick_data(stock, daily_date_list[idx - 1])
                for row in yesterday_tick:
                    row['price'] = today_price
                    row['volume'] = round(row['volume'] * (yesterday_volume / today_volume))
                    row['amount'] = round(row['price'] * row['volume'] * 100)
                yesterday_tick.append(
                    {'': len(yesterday_tick), 'time': '08:00:00', 'price': today_price, 'change': 0, 'volume': 0,
                     'amount': 0, 'type': '中性盘'})
                b = pd.DataFrame(yesterday_tick)
                column_order = ['time', 'price', 'change', 'volume', 'amount', 'type']
                b[column_order].to_csv('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, day))


if __name__ == "__main__":
    all_work_list = []
    if sys.argv[1] == '--day':
        day = sys.argv[2]
        for stock in SYMBOL_LIST:
            date_list = [day]
            all_work_list += generate_work_list(stock, date_list)
    elif sys.argv[1] == '--align':
        p = Pool(POOL_SIZE)
        rs = p.imap_unordered(align_tick_data_stock, SYMBOL_LIST)
        p.close()  # No more work
        list_len = len(SYMBOL_LIST)
        while True:
            completed = rs._index
            if completed == list_len:
                break
            sys.stdout.write('%d/%d\r' % (completed, list_len))
            sys.stdout.flush()
            time.sleep(2)
        sys.stdout.write('%d/%d\r' % (completed, list_len))
        sys.stdout.flush()
        exit()
    else:

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
        sys.stdout.write('%d/%d\r' % (completed, list_len))
        sys.stdout.flush()
        time.sleep(2)
    sys.stdout.write('%d/%d\r' % (completed, list_len))
    sys.stdout.flush()
