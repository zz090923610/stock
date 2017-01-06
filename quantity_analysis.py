#!/usr/bin/python3
from math import log
import pandas as pd
from commom_func import *


def load_tick_data(stock, day):
    data_list = []
    with open('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, day)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_list.append(row)
    return data_list

def load_daily_data(stock):
    data_list = []
    with open('../stock_data/data/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
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


def calculate_trade_quantity_for_stock_one_day(stock, day):
    tick_data = load_tick_data(stock, day)
    buy_small = 0
    buy_large = 0
    sell_small = 0
    sell_large = 0
    mid = 0
    for row in tick_data:
        if row['type'] == '买盘':
            if int(row['volume']) >= 400:
                buy_large += int(row['volume'])
            else:
                buy_small += int(row['volume'])
        elif row['type'] == '卖盘':
            if int(row['volume']) >= 400:
                sell_large += int(row['volume'])
            else:
                sell_small += int(row['volume'])
        else:
            mid += int(row['volume'])
    return buy_small, buy_large, sell_small, sell_large, mid


def calculate_log_quantity_index(stock, base):
    basic_info = load_basic_info_for_stock(stock)
    outstanding = float(basic_info['outstanding']) * 100000000  # 流通股本
    daily_data = load_daily_data(stock)
    result_list = []
    for row in daily_data:
        line = {}
        line['date'] = row['date']
        line['close'] = row['close']
        line['log_quantity'] = log(outstanding / (float(row['volume'])),base)
        result_list.insert(0, line)
    b = pd.DataFrame(result_list)
    column_order = ['date','close', 'log_quantity']
    b[column_order].to_csv('../stock_data/log/%s.csv' % stock, index=False)
