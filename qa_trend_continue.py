#!/usr/bin/python3
# -*- coding: utf-8 -*-
from math import log
from multiprocessing.pool import Pool
from operator import itemgetter
import pandas as pd
import sys

from common_func import *
import numpy as np
import multiprocessing as mp





def load_tick_data(stock, day):
    data_list = []
    with open('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, day)) as csvfile:
        reader = csv.DictReader(csvfile)
        try:
            for row in reader:
                row['price'] = float(row['price'])
                row['volume'] = round(float(row['volume']))
                row['amount'] = round(float(row['amount']))
                data_list.append(row)
        except:
            return []
    return data_list


def calc_average_trade_price_for_stock_one_day(stock, day):
    print('calc ATPD for %s %s' % (stock, day))
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


def load_atpd_data(stock):
    """
    Average Trade Price daily.
    :param stock:
    :return:
    """
    data_list = []
    try:
        with open('../stock_data/qa/atpd/%s.csv' % stock) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['atpd'] = float(row['atpd'])
                data_list.append(row)
        data_new_sorted = sorted(data_list, key=itemgetter('date'))
        return data_new_sorted
    except:
        return []


def calc_average_trade_price_for_stock(stock):
    date_list = load_stock_date_list_from_tick_files(stock)
    atpd_list = load_atpd_data(stock)
    atpd_calced_date_list = [d['date'] for d in atpd_list]
    to_do_date_list = []
    for d in date_list:
        if d not in atpd_calced_date_list:
            to_do_date_list.append(d)
    pool = mp.Pool()
    for i in to_do_date_list:
        pool.apply_async(calc_average_trade_price_for_stock_one_day, args=(stock, i), callback=atpd_list.append)
    pool.close()
    pool.join()
    atpd_list_sorted = sorted(atpd_list, key=itemgetter('date'))
    b = pd.DataFrame(atpd_list_sorted)
    column_order = ['date', 'atpd']
    b[column_order].to_csv('../stock_data/qa/atpd/%s.csv' % stock, index=False)


def calc_atpd_for_all_stock():
    for i in SYMBOL_LIST:
        calc_average_trade_price_for_stock(i)


def calc_atpdr_for_stock(stock):
    print('Calc atpdr for %s' % stock)
    atpd_list = load_atpd_data(stock)
    for (idx, line) in enumerate(atpd_list):
        if idx > 0:
            ratio = line['atpd'] / atpd_list[idx - 1]['atpd']
        else:
            ratio = 1
        line['atpd_ratio'] = '%.4f' % ratio
    b = pd.DataFrame(atpd_list)
    column_order = ['date', 'atpd_ratio']
    b[column_order].to_csv('../stock_data/qa/atpdr/%s.csv' % stock, index=False)


def calc_atpdr_for_all_stock():
    for i in SYMBOL_LIST:
        calc_atpdr_for_stock(i)


def load_atpdr_data(stock):
    """
    Average Trade Price daily.
    :param stock:
    :return:
    """
    data_list = []
    try:
        with open('../stock_data/qa/atpdr/%s.csv' % stock) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['atpd_ratio'] = float(row['atpd_ratio'])
                data_list.append(row)
        data_new_sorted = sorted(data_list, key=itemgetter('date'))
        return data_new_sorted
    except:
        return []


def recent_trend_stat(stock, trade_days, last_day):
    atpdr_list_raw = load_atpdr_data(stock)
    atpdr_list = [i for i in atpdr_list_raw if i['date'] <= last_day]
    if len(atpdr_list) < trade_days:
        select_list = atpdr_list
    else:
        select_list = atpdr_list[len(atpdr_list) - trade_days: len(atpdr_list)]
    td = 0
    if len(atpdr_list) < trade_days:
        return 'up', 0, '1970-01-01'
    for i in range(trade_days):
        if (select_list[-1 - i]['atpd_ratio'] - 1) * (select_list[-1]['atpd_ratio'] - 1) > 0:
            td += 1
            continue
        else:
            break
    if select_list[-1]['atpd_ratio'] > 1:
        return 'up', td, select_list[-1]['date']
    else:
        return 'down', td, select_list[-1]['date']


def sort_trend(trade_days, end_day):
    up_list = []
    down_list = []
    for s in SYMBOL_LIST:
        (trend, continue_day, last_day) = recent_trend_stat(s, trade_days, end_day)
        if (trend == 'up') & (last_day == end_day):
            up_list.append({'code': s, 'trend': trend, 'continue_days': continue_day})
        elif (trend == 'down') & (last_day == end_day):
            down_list.append({'code': s, 'trend': trend, 'continue_days': continue_day})
    return up_list, down_list


def print_trend(trade_days, continue_days, end_day):
    u, d = sort_trend(trade_days, end_day)
    for l in u:
        if l['continue_days'] >= continue_days:
            print(l)
    for l in d:
        if l['continue_days'] >= continue_days:
            print(l)


def load_basic_info_list():
    symbol_dict = {}
    if not os.path.isfile('../stock_data/basic_info.csv'):
        update_basic_info()
    with open('../stock_data/basic_info.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            (y, m, d) = row['timeToMarket'][0:4], row['timeToMarket'][4:6], row['timeToMarket'][6:8]
            symbol_dict[row['code']] = {'timeToMarket': '%s-%s-%s' % (y, m, d), 'name': row['name']}
    return symbol_dict


def generate_trend_report(trade_days, continue_days, end_day):
    basic_info_list = load_basic_info_list()
    msg = u'%s\n连续五日日平均交易价格上涨股票\n' % end_day
    u, d = sort_trend(trade_days, end_day)
    for l in u:
        l['timeToMarket'] = basic_info_list[l['code']]['timeToMarket']
    for l in d:
        l['timeToMarket'] = basic_info_list[l['code']]['timeToMarket']
    u = sorted(u, key=itemgetter('timeToMarket'))
    d = sorted(d, key=itemgetter('timeToMarket'))
    for l in u:
        if l['continue_days'] >= continue_days:
            msg += u'连续 %s 天上涨 [%s] %s %s 上市\n' % (l['continue_days'], l['code'], basic_info_list[l['code']]['name'],
                                                   basic_info_list[l['code']]['timeToMarket'])
    msg += u'\n连续五日日平均交易价格下跌股票\n'
    for l in d:
        if l['continue_days'] >= continue_days:
            msg += u'连续 %s 天下跌 [%s] %s %s 上市\n' % (l['continue_days'], l['code'], basic_info_list[l['code']]['name'],
                                                   basic_info_list[l['code']]['timeToMarket'])
    with open('../stock_data/report/five_days_trend/%s.txt' % end_day, 'wb') as myfile:
        myfile.write(bytes(msg, encoding='utf-8'))


if __name__ == '__main__':
    calc_atpd_for_all_stock()
    calc_atpdr_for_all_stock()
    generate_trend_report(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
