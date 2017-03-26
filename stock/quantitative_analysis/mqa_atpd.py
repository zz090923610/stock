#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess

from scoop import futures

from stock.common.common_func import *
from stock.common.communction import simple_publish
from stock.common.time_util import load_stock_date_list_from_tick_files

data = BASIC_INFO.symbol_list
REFRESH_ATPD = False


def calc_average_trade_price_for_stock_one_day_pd(stock, day):
    try:
        df = pd.read_csv('%s/tick_data/%s/%s_%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock, stock, day))
    except FileNotFoundError:
        return
    outstanding = float(BASIC_INFO.outstanding_dict[stock]) * 100000000.
    large_threshold = outstanding / 3600000

    tick_buy = df[df['type'] == '买盘']
    tick_sell = df[df['type'] == '卖盘']
    tick_buy_large = tick_buy[tick_buy['volume'] >= large_threshold]
    tick_sell_large = tick_sell[tick_sell['volume'] >= large_threshold]
    tick_buy_small = tick_buy[tick_buy['volume'] < large_threshold]
    tick_sell_small = tick_sell[tick_sell['volume'] < large_threshold]

    vol_sum = sum(df['volume'])
    vol_buy_large_sum = sum(tick_buy_large['volume'])
    vol_sell_large_sum = sum(tick_sell_large['volume'])
    vol_buy_small_sum = sum(tick_buy_small['volume'])
    vol_sell_small_sum = sum(tick_sell_small['volume'])
    cost_sum = sum(df['volume'] * df['price'])
    tvi = sum(tick_buy['volume']) - sum(tick_sell['volume'])
    tvi_large = sum(tick_buy_large['volume']) - sum(tick_sell_large['volume'])
    tvi_small = sum(tick_buy_small['volume']) - sum(tick_sell_small['volume'])
    tmi = sum(tick_buy['volume'] * tick_buy['price'] * 100) - sum(tick_sell['volume'] * tick_sell['price'] * 100)
    tmi_large = sum(tick_buy_large['volume'] * tick_buy_large['price'] * 100) - sum(
        tick_sell_large['volume'] * tick_sell_large['price'] * 100)
    tmi_small = sum(tick_buy_small['volume'] * tick_buy_small['price'] * 100) - sum(
        tick_sell_small['volume'] * tick_sell_small['price'] * 100)
    try:
        atpd = '%.2f' % (cost_sum / vol_sum)
    except ZeroDivisionError:
        atpd = 0
    try:
        vls_ratio = (vol_buy_large_sum + vol_sell_large_sum) / (vol_buy_small_sum + vol_sell_small_sum)
    except ZeroDivisionError:
        vls_ratio = 1
    tick_size = len(df)
    return {'date': day, 'atpd': atpd, 'vol_buy_large_sum': vol_buy_large_sum, 'vol_buy_small_sum': vol_buy_small_sum,
            'vol_sell_large_sum': vol_sell_large_sum, 'vol_sell_small_sum': vol_sell_small_sum, 'tvi': tvi,
            'tvi_large': tvi_large, 'tvi_small': tvi_small, 'tmi': float('%.2f' % (tmi / 10000)),
            'tmi_large': float('%.2f' % (tmi_large / 10000)), 'tmi_small': float('%.2f' % (tmi_small / 10000)),
            'volume_sum': vol_sum, 'cost_sum': float('%.2f' % cost_sum), 'tick_size': tick_size, 'vls_ratio': vls_ratio}


# noinspection PyShadowingNames
def calc_average_trade_price_for_stock(idx):
    stock = data[idx]
    column_order = ['date', 'atpd', 'vol_buy_large_sum', 'vol_buy_small_sum', 'vol_sell_large_sum',
                    'vol_sell_small_sum', 'tvi', 'tvi_large', 'tvi_small', 'tmi', 'tmi_large', 'tmi_small',
                    'volume_sum',
                    'cost_sum', 'tick_size', 'vls_ratio']
    date_list = load_stock_date_list_from_tick_files(stock)
    try:
        df = pd.read_csv('%s/quantitative_analysis/atpd/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock))
    except FileNotFoundError:
        df = pd.DataFrame(columns=column_order)
    atpd_calced_date_list = df['date'].tolist()
    to_do_date_list = list(set(date_list).difference(set(atpd_calced_date_list)))

    if len(to_do_date_list) == 0:
        print('atpd for %s updated' % stock)
        return
    print('calc atpd for %s' % stock)

    tmp = []
    for i in to_do_date_list:
        tmp.append(calc_average_trade_price_for_stock_one_day_pd(stock, i))

    tmp = pd.DataFrame(tmp)
    df = pd.concat([df, tmp])
    try:
        df = df.drop('index', 1)
    except ValueError:
        pass
    df = df.drop_duplicates('date', keep='last')
    df = df.sort_values(by='date')
    df = df.reset_index()
    df[column_order].to_csv('%s/quantitative_analysis/atpd/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock),
                            index=False)
    simple_publish('qa_update','atpd_%s' % stock)


# noinspection PyShadowingNames
def calc_atpd():
    simple_publish('qa_update','atpd_start')
    if not os.path.isdir('%s/quantitative_analysis/atpd' % COMMON_VARS_OBJ.stock_data_root):
        os.makedirs('%s/quantitative_analysis/atpd' % COMMON_VARS_OBJ.stock_data_root)
    # FIXME buggy multi processing when re calculated

    pool = mp.Pool()
    # noinspection PyShadowingNames
    for (idx, stock) in enumerate(BASIC_INFO.symbol_list):
        pool.apply_async(calc_average_trade_price_for_stock, args=(idx,))
    pool.close()
    pool.join()
    simple_publish('qa_update','atpd_finished')

if __name__ == '__main__':
    if not os.path.isdir('%s/quantitative_analysis/atpd' % COMMON_VARS_OBJ.stock_data_root):
        os.makedirs('%s/quantitative_analysis/atpd' % COMMON_VARS_OBJ.stock_data_root)
    # FIXME buggy multi processing when re calculated
    # results = list(futures.map(calc_average_trade_price_for_stock, range(len(data))))

    pool = mp.Pool()
    # noinspection PyShadowingNames
    for (idx, stock) in enumerate(BASIC_INFO.symbol_list):
        pool.apply_async(calc_average_trade_price_for_stock, args=(idx,))
    pool.close()
    pool.join()
