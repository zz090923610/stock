#!/usr/bin/python3
# -*- coding: utf-8 -*-
from math import log
from multiprocessing.pool import Pool
from operator import itemgetter
import pandas as pd
import sys

import subprocess

from common_func import *
import numpy as np
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


def load_adl_data(stock):
    data_list = []
    with open('../stock_data/qa/adl/%s.csv' % stock) as csvfile:
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


def calculate_adl_for_stock(stock):
    subprocess.call("mkdir -p %s/qa/adl" % stock_data_root, shell=True)
    daily_data = load_daily_data(stock)
    for (idx, line) in enumerate(daily_data):
        try:
            item = ((line['close'] - line['low']) - (line['high'] - line['close'])) / (line['high'] - line['low']) * \
                   line['volume']
        except ZeroDivisionError:
            if idx == 0:
                item = ((line['close'] - line['low']) - (line['high'] - line['close'])) * line['volume']
            while idx > 0:
                try:
                    item = ((line['close'] - line['low']) - (line['high'] - line['close'])) / (
                        daily_data[idx - 1]['high'] -
                        daily_data[idx - 1]['low']) * \
                           line['volume']
                    break
                except ZeroDivisionError:
                    idx -= 1
        item = round(item)
        if idx == 0:
            line['adl'] = item
        else:
            line['adl'] = item + daily_data[idx - 1]['adl']
    daily_data_sorted = sorted(daily_data, key=itemgetter('date'))
    b = pd.DataFrame(daily_data_sorted)
    column_order = ['date', 'open', 'high', 'close', 'low', 'adl']
    b[column_order].to_csv('../stock_data/qa/adl/%s.csv' % stock, index=False)
    return daily_data_sorted


def update_adl():
    pool = mp.Pool()
    for i in SYMBOL_LIST:
        pool.apply_async(calculate_adl_for_stock, args=(i,))
    pool.close()
    pool.join()


if __name__ == '__main__':
    update_adl()
