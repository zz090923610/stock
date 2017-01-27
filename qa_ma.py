#!/usr/bin/python3
# Moving Average System

import subprocess
import multiprocessing as mp
import sys

from common_func import *
from qa_trend_continue import load_atpd_data
from variables import *


class ma_align:
    def __init__(self, stock, ma_select=None):
        if ma_select is None:
            ma_select = ['day_long', 'quarter_short', 'quarter_long']
        self.ma_select = ma_select
        self.ma_day_short = (6, 'atpd')
        self.ma_day_long = (13, 'atpd')
        self.ma_quarter_short = (27, 'atpd')
        self.ma_quarter_long = (73, 'atpd')
        self.ma_year_short = (140, 'atpd')
        self.ma_year_long = (260, 'atpd')
        self.stock=stock
        self.



def save_ma_for_stock(stock, ma_list, ma_params):
    subprocess.call("mkdir -p %s/qa/ma/%s" % (stock_data_root, ma_params), shell=True)
    with open("%s/qa/ma/%s/%s.pickle" % (stock_data_root, ma_params, stock), 'wb') as f:
        pickle.dump(ma_list, f, -1)


def calc_ma_for_stock(stock, days, type='atpd'):
    """
    :param stock:
    :param days:
    :param type:'close', 'atpd'
    :return:
    """

    days = int(days)
    print('Calc %d days %s Moving Average for stock %s' % (days, type, stock))
    data_list = []
    assert days > 0
    if type == 'close':
        # data_list = close data of a stock
        data_list = load_daily_data(stock)
    elif type == 'atpd':
        # data_list = average trade price of day data of a stock
        data_list = load_atpd_data(stock)
    if len(data_list) < days:
        return
    ma_list = []
    for (idx, line) in enumerate(data_list):
        if idx < days - 1:
            ma_list.append({'date': line['date'], 'ma%d' % days: None})
        ma5 = sum(float(i[type]) for i in data_list[idx - days + 1: idx + 1]) / days
        ma_list.append({'date': line['date'], 'ma%d' % days: '%.3f' % ma5})
    save_ma_for_stock(stock, ma_list, '%s_%d' % (type, days))
    return ma_list


def calc_ma_for_all_stock(days, type='atpd'):
    pool = mp.Pool()
    for i in SYMBOL_LIST:
        pool.apply_async(calc_ma_for_stock, args=(i, days, type))
    pool.close()
    pool.join()





if __name__ == '__main__':
    calc_ma_for_all_stock(sys.argv[1], sys.argv[2])
