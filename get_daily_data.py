#!/usr/bin/env python3
import os
import pandas as pd
from pathlib import Path
from time import sleep
import sys
import os.path
from multiprocessing import Pool
from operator import itemgetter
from common_func import *


def get_all_data_for_one_stock(stock):
    print('getting %s' % stock)
    start = max(BASIC_INFO.time_to_market_dict[stock], START_DATE)
    my_file = Path('../stock_data/data/%s.csv' % stock)
    if my_file.is_file():
        get_update_for_one_stock(stock)
        return
    data = ts.get_k_data(stock, autype='qfq', start=start, end=get_today())
    data = data.reindex(index=data.index[::-1])
    cols = ['date', 'open', 'high', 'close', 'low', 'volume']
    data[cols].to_csv('../stock_data/data/%s.csv' % stock, index=False)
    data_non_fq = ts.get_k_data(stock, autype='None', start=start, end=get_today())
    data_non_fq = data_non_fq.reindex(index=data.index[::-1])
    data_non_fq[cols].to_csv('../stock_data/data/%s_non_fq.csv' % stock, index=False)


def get_all_data_for_all_stock():
    print('here')
    p = Pool(64)
    rs = p.imap_unordered(get_all_data_for_one_stock, BASIC_INFO.symbol_list)
    p.close()  # No more work
    list_len = len(BASIC_INFO.symbol_list)
    while True:
        completed = rs._index
        if completed == list_len:
            break
        sys.stdout.write('Getting %.3f\n' % (completed / list_len))
        sys.stdout.flush()
        sleep(2)
    sys.stdout.write('Getting 1.000\n')
    sys.stdout.flush()


def get_update_for_one_stock(stock):
    if not os.path.isfile('../stock_data/data/%s.csv' % stock):
        get_all_data_for_one_stock(stock)
    start = max(BASIC_INFO.time_to_market_dict[stock], START_DATE)
    all_date_list = get_stock_open_date_list(start)
    date_list_already_have = load_stock_date_list_from_daily_data(stock)
    trade_pause_list = load_trade_pause_date_list_for_stock(stock)
    data_already_have = []
    data_non_fq_already_have = []
    with open('../stock_data/data/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_already_have.append(row)
    with open('../stock_data/data/%s_non_fq.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_non_fq_already_have.append(row)
    for day in all_date_list:
        if day in date_list_already_have:
            continue
        elif day in trade_pause_list:
            continue
        else:
            print('Missing day %s for %s' % (day, stock))
            data = ts.get_k_data(stock, autype='qfq', start=day, end=day)
            data_non_fq = ts.get_k_data(stock, autype='None', start=day, end=day)
            if data.empty:
                if (max(MARKET_OPEN_DATE_LIST) != get_today()) & (day == get_today()):
                    pass
                else:
                    trade_pause_list.append(day)
                    save_trade_pause_date_date_list_for_stock(stock, trade_pause_list)
                continue
            cols = ['date', 'open', 'high', 'close', 'low', 'volume']
            data = data.reindex(index=data.index[::-1])
            data[cols].to_csv('../stock_data/data/tmp_%s.csv' % stock, index=False)
            with open('../stock_data/data/tmp_%s.csv' % stock) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data_already_have.append(row)
            data_new_sorted = sorted(data_already_have, key=itemgetter('date'), reverse=True)
            b = pd.DataFrame(data_new_sorted)
            column_order = ['date', 'open', 'high', 'close', 'low', 'volume']
            b[column_order].to_csv('../stock_data/data/%s.csv' % stock, index=False)
            os.remove('../stock_data/data/tmp_%s.csv' % stock)

            data_non_fq = data_non_fq.reindex(index=data.index[::-1])
            data_non_fq[cols].to_csv('../stock_data/data/tmp_non_fq_%s.csv' % stock, index=False)
            with open('../stock_data/data/tmp_non_fq_%s.csv' % stock) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data_non_fq_already_have.append(row)
            data_non_fq_already_have_sorted = sorted(data_non_fq_already_have, key=itemgetter('date'), reverse=True)
            b = pd.DataFrame(data_non_fq_already_have_sorted)
            column_order = ['date', 'open', 'high', 'close', 'low', 'volume']
            b[column_order].to_csv('../stock_data/data/%s_non_fq.csv' % stock, index=False)
            os.remove('../stock_data/data/tmp_non_fq_%s.csv' % stock)


def handle_update_one(stock):
    try:
        get_update_for_one_stock(stock)
    except:
        get_all_data_for_one_stock(stock)


def get_update_for_all_stock():
    p = Pool(64)
    rs = p.imap_unordered(handle_update_one, BASIC_INFO.symbol_list)
    p.close()  # No more work
    list_len = len(BASIC_INFO.symbol_list)
    while True:
        completed = rs._index
        if completed == list_len:
            break
        sys.stdout.write('Getting %.3f\n' % (completed / list_len))
        sys.stdout.flush()
        sleep(2)
    sys.stdout.write('Getting 1.000\n')
    sys.stdout.flush()


if __name__ == "__main__":
    fetch_type = 'all'
    for loop in range(1, len(sys.argv)):
        if sys.argv[loop] == '--all':
            fetch_type = 'all'
        elif sys.argv[loop] == '--update':
            fetch_type = 'update'
    if fetch_type == 'all':
        get_all_data_for_all_stock()
    elif fetch_type == 'update':
        get_update_for_all_stock()
