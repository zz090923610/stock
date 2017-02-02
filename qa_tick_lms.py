#!/usr/bin/python3
# -*- coding: utf-8 -*-
from math import log
from multiprocessing.pool import Pool
from operator import itemgetter

import matplotlib
import pandas as pd
import sys

from common_func import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.finance as plfin
import matplotlib.ticker as ticker


def calc_tick_related_for_stock_one_day(stock, day, normalize=False, scaler=1):
    basic_info = BASIC_INFO_DICT[stock]
    outstanding = float(basic_info['outstanding']) * 100000000.  # 流通股本
    large_threshold = outstanding / 3600000
    mid_threshold = outstanding / 18000000
    tick_data = load_tick_data(stock, day, scaler=scaler)
    (buy_small, sell_small) = (0, 0)
    (buy_mid, sell_mid) = (0, 0)
    (buy_large, sell_large) = (0, 0)
    undirected_trade = 0
    vol_sum = 0
    cost_sum = 0
    for row in tick_data:
        cost_sum += row['price'] * row['volume']
        vol_sum += row['volume']
        if row['type'] == '买盘':
            if int(row['volume']) >= large_threshold:
                buy_large += row['volume']
            elif (int(row['volume']) >= mid_threshold) & (int(row['volume']) < large_threshold):
                buy_mid += row['volume']
            else:
                buy_small += row['volume']
        elif row['type'] == '卖盘':
            if row['volume'] >= large_threshold:
                sell_large += row['volume']
            elif (int(row['volume']) >= mid_threshold) & (int(row['volume']) < large_threshold):
                sell_mid += row['volume']
            else:
                sell_small += row['volume']
    try:
        atpd = '%.2f' % (cost_sum / vol_sum)
    except ZeroDivisionError:
        atpd = -1
    result = {'date': day, 'atpd': atpd}

    if normalize:
        result.update(
            dict(buy_large=buy_large / outstanding, sell_large=sell_large / outstanding, buy_mid=buy_mid / outstanding,
                 sell_mid=sell_mid / outstanding, buy_small=buy_small / outstanding,
                 sell_small=sell_small / outstanding, undirected_trade=undirected_trade / outstanding))
    else:
        result.update(
            dict(buy_large=buy_large, sell_large=sell_large, buy_mid=buy_mid, sell_mid=sell_mid, buy_small=buy_small,
                 sell_small=sell_small, undirected_trade=undirected_trade / outstanding))
    return result


def calculate_lms_for_stock_one_day(stock, day, normalize=False):
    basic_info = BASIC_INFO_DICT[stock]
    outstanding = float(basic_info['outstanding']) * 100000000.  # 流通股本
    large_threshold = outstanding / 3600000
    mid_threshold = outstanding / 18000000
    tick_data = load_tick_data(stock, day)
    (buy_small, sell_small) = (0, 0)
    (buy_mid, sell_mid) = (0, 0)
    (buy_large, sell_large) = (0, 0)
    undirected_trade = 0
    for row in tick_data:
        if row['type'] == '买盘':
            if int(row['volume']) >= large_threshold:
                buy_large += row['volume']
            elif (int(row['volume']) >= mid_threshold) & (int(row['volume']) < large_threshold):
                buy_mid += row['volume']
            else:
                buy_small += row['volume']
        elif row['type'] == '卖盘':
            if row['volume'] >= large_threshold:
                sell_large += row['volume']
            elif (int(row['volume']) >= mid_threshold) & (int(row['volume']) < large_threshold):
                sell_mid += row['volume']
            else:
                sell_small += row['volume']
    if normalize:

        return buy_large / outstanding, sell_large / outstanding, buy_mid / outstanding, sell_mid / outstanding, \
               buy_small / outstanding, sell_small / outstanding, undirected_trade / outstanding
    else:
        return buy_large, sell_large, buy_mid, sell_mid, buy_small, sell_small, undirected_trade


def load_lms(stock):
    lms_data = []
    with open('../stock_data/qa/lms/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['buy_large'] = int(row['buy_large'])
            row['sell_large'] = int(row['sell_large'])
            row['buy_mid'] = int(row['buy_mid'])
            row['sell_mid'] = int(row['sell_mid'])
            row['buy_small'] = int(row['buy_small'])
            row['sell_small'] = int(row['sell_small'])
            row['undirected_trade'] = int(row['undirected_trade'])
            lms_data.append(row)
    data_new_sorted = sorted(lms_data, key=itemgetter('date'))
    return data_new_sorted


def calc_lms_for_stock(stock):
    date_list = load_stock_date_list_from_daily_data(stock)
    detailed_trade_list = []
    for day in date_list:
        (buy_large, sell_large, buy_mid, sell_mid, buy_small, sell_small,
         undirected_trade) = calculate_lms_for_stock_one_day(stock, day)
        line = dict(date=day, buy_large=buy_large, sell_large=sell_large, buy_mid=buy_mid, sell_mid=sell_mid,
                    buy_small=buy_small, sell_small=sell_small, undirected_trade=undirected_trade)
        detailed_trade_list.append(line)
    b = pd.DataFrame(detailed_trade_list)
    column_order = ['date', 'buy_large', 'sell_large', 'buy_mid', 'sell_mid', 'buy_small', 'sell_small',
                    'undirected_trade']
    b[column_order].to_csv('../stock_data/qa/lms/%s.csv' % stock, index=False)
    return detailed_trade_list


def update_lms_trade_for_stock_for_day(stock, day):
    if not os.path.exists('../stock_data/qa/lms/%s.csv' % stock):
        calc_lms_for_stock(stock)
    if not os.path.exists('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, day)):
        return
    (buy_large, sell_large, buy_mid, sell_mid, buy_small, sell_small,
     undirected_trade) = calculate_lms_for_stock_one_day(stock, day)
    lms = load_lms(stock)
    lms_date_list = [lms[x]['date'] for x in range(0, len(lms))]
    if day in lms_date_list:
        return
    line = {'date': day, 'buy_large': buy_large,
            'sell_large': sell_large,
            'buy_mid': buy_mid,
            'sell_mid': sell_mid,
            'buy_small': buy_small,
            'sell_small': sell_small,
            'undirected_trade': undirected_trade}
    lms.append(line)
    sorted_lms = sorted(lms, key=itemgetter('date'), reverse=True)
    b = pd.DataFrame(sorted_lms)
    column_order = ['date', 'buy_large', 'sell_large', 'buy_mid', 'sell_mid', 'buy_small', 'sell_small',
                    'undirected_trade']
    b[column_order].to_csv('../stock_data/qa/lms/%s.csv' % stock, index=False)


def calc_lms_for_all_stock():
    p = Pool(8)
    rs = p.imap_unordered(calc_lms_for_stock, SYMBOL_LIST)
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


if __name__ == '__main__':
    calc_lms_for_all_stock()
