#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

from common_func import *
from scoop import futures

data = BASIC_INFO.symbol_list


def calc_average_trade_price_for_stock_one_day(stock, day):
    tick_day = load_tick_data(stock, day)
    vol_sum = 0
    cost_sum = 0
    for line in tick_day:
        cost_sum += line['price'] * line['volume']
        vol_sum += line['volume']
    try:
        result = '%.2f' % (cost_sum / vol_sum)
    except ZeroDivisionError:
        result = -1
    return {'date': day, 'atpd': result}


def calc_average_trade_price_for_stock(idx):
    stock = data[idx]
    date_list = load_stock_date_list_from_tick_files(stock)
    atpd_list = []
    if len(date_list) == 0:
       return
    print('calc atpd for %s' % stock)
    for i in date_list:
       atpd_list.append(calc_average_trade_price_for_stock_one_day(stock, i))
    atpd_list_sorted = sorted(atpd_list, key=itemgetter('date'))
    b = pd.DataFrame(atpd_list_sorted)
    column_order = ['date', 'atpd']
    b[column_order].to_csv('../stock_data/qa/atpd/%s.csv' % stock, index=False)


if __name__ == '__main__':
    results = list(futures.map(calc_average_trade_price_for_stock, range(len(data))))
