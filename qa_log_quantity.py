#!/usr/bin/python3
# -*- coding: utf-8 -*-
from math import log
from multiprocessing.pool import Pool

import matplotlib
import pandas as pd
import sys

from common_func import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.finance as plfin
import matplotlib.ticker as ticker



def load_detailed_daily_trade_data(stock):
    data_list = []
    with open('../stock_data/detailed_daily_trade_data/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['buy_small'] = float(row['buy_small'])
            row['buy_large'] = float(row['buy_large'])
            row['sell_small'] = float(row['sell_small'])
            row['sell_large'] = float(row['sell_large'])
            row['mid'] = float(row['mid'])
            data_list.append(row)
    return data_list



def calculate_trade_quantity_for_stock_one_day(stock, day):
    basic_info = BASIC_INFO_DICT[stock]
    outstanding = float(basic_info['outstanding']) * 100000000.  # 流通股本
    large_threshold = outstanding / 3600000
    tick_data = load_tick_data(stock, day)
    buy_small = 0
    buy_large = 0
    sell_small = 0
    sell_large = 0
    mid = 0
    for row in tick_data:
        if row['type'] == '买盘':
            if int(row['volume']) >= large_threshold:
                buy_large += row['volume']
            else:
                buy_small += row['volume']
        elif row['type'] == '卖盘':
            if row['volume'] >= large_threshold:
                sell_large += row['volume']
            else:
                sell_small += row['volume']
    return buy_small, buy_large, sell_small, sell_large, mid


def calculate_detailed_trade_quantity_for_stock(stock):
    date_list = load_stock_date_list_from_daily_data(stock)
    detailed_trade_list = []
    for day in date_list:
        (buy_small, buy_large, sell_small, sell_large, mid) = calculate_trade_quantity_for_stock_one_day(stock, day)
        line = {'date': day, 'buy_small': buy_small, 'buy_large': buy_large, 'sell_small': sell_small,
                'sell_large': sell_large, 'mid': mid}
        detailed_trade_list.insert(0, line)
    b = pd.DataFrame(detailed_trade_list)
    column_order = ['date', 'buy_small', 'buy_large', 'sell_small',
                    'sell_large', 'mid']
    b[column_order].to_csv('../stock_data/detailed_daily_trade_data/%s.csv' % stock, index=False)


def calculate_log_quantity_index(stock, base):
    basic_info = BASIC_INFO_DICT[stock]
    outstanding = float(basic_info['outstanding']) * 100000000.  # 流通股本
    daily_data = load_daily_data(stock)
    detailed_daily_trade_data = load_detailed_daily_trade_data(stock)
    result_list = []
    for (idx,row) in enumerate(daily_data):
        line = {'date': row['date'], 'high': row['high'], 'low': row['low'], 'open': row['open'], 'close': row['close'],
                'log_quantity': log(outstanding / (row['volume']), base),
                'log_buy_large': log(outstanding / (detailed_daily_trade_data[idx]['buy_large']+1), base),
                'log_buy_small': log(outstanding / (detailed_daily_trade_data[idx]['buy_small']+1), base),
                'log_sell_large': log(outstanding / (detailed_daily_trade_data[idx]['sell_large']+1), base),
                'log_sell_small': log(outstanding / (detailed_daily_trade_data[idx]['sell_small']+1), base)
                }
        result_list.insert(0, line)
    b = pd.DataFrame(result_list)
    column_order = ['date', 'close', 'log_quantity', 'log_buy_large', 'log_buy_small','log_sell_large','log_sell_small' ]
    b[column_order].to_csv('../stock_data/log/%s.csv' % stock, index=False)
    return result_list


def plot_log_quantity_idx(stock, base, type):
    basic_info = BASIC_INFO_DICT[stock]
    a = calculate_log_quantity_index(stock, base)
    closes = []
    opens = []
    highs = []
    lows = []
    log_quantity = []
    log_buy_large=[]
    log_buy_small = []
    log_sell_large = []
    log_sell_small= []
    date_list = []
    for row in a:
        opens.append(row['open'])
        closes.append(row['close'])
        highs.append(row['high'])
        lows.append(row['low'])
        log_quantity.append(row['log_quantity'])
        log_buy_large.append(row['log_buy_large'])
        log_buy_small.append(row['log_buy_small'])
        log_sell_large.append(row['log_sell_large'])
        log_sell_small.append(row['log_sell_small'])
        date_list.append(row['date'])
    fig, ax1 = plt.subplots()
    matplotlib.rcParams.update({'font.size': 22})
    N = len(date_list)
    ind = np.arange(N)
    def format_date(x, pos=None):
        thisind = np.clip(int(x + 0.5), 0, N - 1)
        return date_list[thisind]

    legend_list = []
    assert (len(ind) == len(closes))
    if type.find('overall') != -1:
        oa, = ax1.plot(ind, log_quantity, '-', label=u'综合')
        plt.setp(oa, linewidth=2)
        legend_list.append(oa)
    if type.find('buy_large')!= -1:
        bl, = ax1.plot(ind, log_buy_large, '-', label=u'大买')
        plt.setp(bl, linewidth=2)
        legend_list.append(bl)
    if type.find('sell_large') != -1:
        sl, = ax1.plot(ind, log_sell_large, '-', label=u'大卖')
        plt.setp(sl, linewidth=2)
        legend_list.append(sl)
    if type.find('buy_small') != -1:
        bs, = ax1.plot(ind, log_buy_small, '-', label=u'小买')
        plt.setp(bs, linewidth=2)
        legend_list.append(bs)
    if type.find('sell_small')!= -1:
        ss, = ax1.plot(ind, log_sell_small, '-', label=u'小卖')
        plt.setp(ss, linewidth=2)
        legend_list.append(ss)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
    leg = plt.legend(handles=legend_list)
    leg.get_frame().set_alpha(0.5)
    plt.xlabel('%s %s'%(stock, basic_info['name']))
    if type.find('kline') != -1:
        ax2 = ax1.twinx()
        plfin.candlestick2_ochl(ax2, opens, closes, highs, lows, width=0.75, colorup='r', colordown='g', alpha=1)

    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    fig.autofmt_xdate()
    #return date_list, opens, closes, highs, lows

if __name__ == '__main__':
    p = Pool(8)
    rs = p.imap_unordered(calculate_detailed_trade_quantity_for_stock, BASIC_INFO.symbol_list)
    p.close()  # No more work
    list_len = len(BASIC_INFO.symbol_list)
    while True:
        completed = rs._index
        if completed == list_len:
            break
        sys.stdout.write('%d/%d\r' % (completed, list_len))
        sys.stdout.flush()
        time.sleep(2)
    sys.stdout.write('%d/%d\r' % (completed, list_len))
    sys.stdout.flush()