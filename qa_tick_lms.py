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


def load_tick_data(stock, day):
    data_list = []
    with open('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, day)) as csvfile:
        reader = csv.DictReader(csvfile)
        try:
            for row in reader:
                row['price'] = float(row['price'])
                row['volume'] = int(row['volume'])
                row['amount'] = int(row['amount'])
                data_list.append(row)
        except:
            return []
    return data_list


def load_daily_data(stock):
    data_list = []
    with open('../stock_data/data/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['open'] = float(row['open'])
            row['high'] = float(row['high'])
            row['close'] = float(row['close'])
            row['low'] = float(row['low'])
            row['volume'] = float(row['volume'])
            data_list.append(row)
    return data_list


def load_basic_info_for_stock(stock):
    basic_info_list = []
    with open('../stock_data/basic_info.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            basic_info_list.append(row)
    basic_info = None
    for row in basic_info_list:
        if row['code'] == stock:
            basic_info = row
    return basic_info


def print_basic_info(stock):
    basic_info = load_basic_info_for_stock(stock)
    print('代码: {} 名称: {} 所属行业: {} 地区: {} \n\
市盈率: {} 流通股本(亿): {} 总股本(亿): {} 总资产(万): {} \n\
流动资产: {} 固定资产: {} 公积金: {} 每股公积金: {} 每股收益: {} \n\
每股净资: {} 市净率: {} 上市日期: {} 未分利润: {} 每股未分配: {}\n\
收入同比(%): {} 利润同比(%): {} 毛利率(%): {} 净利润率(%): {} 股东人数: {}'
          .format(basic_info['code'],
                  basic_info['name'],
                  basic_info['industry'],
                  basic_info['area'],
                  basic_info['pe'],
                  basic_info['outstanding'],
                  basic_info['totals'],
                  basic_info['totalAssets'],
                  basic_info['liquidAssets'],
                  basic_info['fixedAssets'],
                  basic_info['reserved'],
                  basic_info['reservedPerShare'],
                  basic_info['esp'],
                  basic_info['bvps'],
                  basic_info['pb'],
                  basic_info['timeToMarket'],
                  basic_info['undp'],
                  basic_info['perundp'],
                  basic_info['rev'],
                  basic_info['profit'],
                  basic_info['gpr'],
                  basic_info['npr'],
                  basic_info['holders']))


def calculate_lms_for_stock_one_day(stock, day):
    basic_info = load_basic_info_for_stock(stock)
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
    return buy_large, sell_large, buy_mid, sell_mid, buy_small, sell_small, undirected_trade


def load_lms(stock):
    lms_data = []
    with open('../stock_data/qa/lms/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['buy_large']= int(row['buy_large'])
            row['sell_large'] = int(row['sell_large'])
            row['buy_mid'] = int(row['buy_mid'])
            row['sell_mid'] = int(row['sell_mid'])
            row['buy_small'] = int(row['buy_small'])
            row['sell_small']= int(row['sell_small'])
            row['undirected_trade'] = int(row['undirected_trade'])
            lms_data.append(row)
    return lms_data


def generated_lms_trade_for_stock(stock):
    date_list = load_stock_date_list_from_daily_data(stock)
    detailed_trade_list = []
    for day in date_list:
        (buy_large, sell_large, buy_mid, sell_mid, buy_small, sell_small,
         undirected_trade) = calculate_lms_for_stock_one_day(stock, day)
        line = {'date': day, 'buy_large': buy_large,
                'sell_large': sell_large,
                'buy_mid': buy_mid,
                'sell_mid': sell_mid,
                'buy_small': buy_small,
                'sell_small': sell_small,
                'undirected_trade': undirected_trade}
        detailed_trade_list.insert(0, line)
    sorted_lms = sorted(detailed_trade_list, key=itemgetter('date'), reverse=True)
    b = pd.DataFrame(sorted_lms)
    column_order = ['date', 'buy_large', 'sell_large', 'buy_mid', 'sell_mid', 'buy_small', 'sell_small',
                    'undirected_trade']
    b[column_order].to_csv('../stock_data/qa/lms/%s.csv' % stock, index=False)


def update_lms_trade_for_stock_for_day(stock, day):
    if not os.path.exists('../stock_data/qa/lms/%s.csv' % stock):
        generated_lms_trade_for_stock(stock)
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


if __name__ == '__main__':
    p = Pool(8)
    rs = p.imap_unordered(generated_lms_trade_for_stock, SYMBOL_LIST)
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
