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
import multiprocessing as mp


def load_daily_data(stock):
    data_list = []
    with open('../stock_data/data/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['open'] = float(row['open'])
            row['high'] = float(row['high'])
            row['close'] = float(row['close'])
            row['low'] = float(row['low'])
            row['volume'] = round(float(row['volume']))
            data_list.append(row)
    data_new_sorted = sorted(data_list, key=itemgetter('date'))
    return data_new_sorted


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


def calculate_vhf(stock, n):
    daily_data = load_daily_data(stock)
    close_price_list = [d['close'] for d in daily_data]
    for (idx, data_for_day) in enumerate(daily_data):
        if idx < n:
            data_for_day['vhf'] = '-'
        else:
            hcp = max(close_price_list[idx - n + 1: idx + 1])
            lcp = min(close_price_list[idx - n + 1: idx + 1])
            numerator = abs(hcp - lcp)
            denominator = 0
            for i in range(0, n):
                denominator += abs(close_price_list[idx - i] - close_price_list[idx - i - 1])
            vhf = numerator / denominator
            data_for_day['vhf'] = vhf
    b = pd.DataFrame(daily_data)
    column_order = ['date', 'close', 'vhf']
    b[column_order].to_csv('../stock_data/qa/vhf/%s.csv' % stock, index=False)
    return daily_data


if __name__ == '__main__':
    pool = mp.Pool()
    for i in SYMBOL_LIST:
        pool.apply_async(calculate_vhf, args=(i, 5))
    pool.close()
    pool.join()
