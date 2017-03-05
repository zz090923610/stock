#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

from stock.common.common_func import *
from scoop import futures

data = BASIC_INFO.symbol_list
REFRESH_ATPD = False


# noinspection PyShadowingNames
def calc_average_trade_price_for_stock_one_day(stock, day):
    tick_day = load_tick_data(stock, day)
    vol_sum = 0
    vol_buy_large_sum = 0
    vol_buy_small_sum = 0
    vol_sell_large_sum = 0
    vol_sell_small_sum = 0
    cost_sum = 0
    tvi = 0
    tvi_large = 0
    tmi = 0
    tmi_large = 0
    tvi_small = 0
    tmi_small = 0
    direction = 'a'
    outstanding = float(BASIC_INFO.outstanding_dict[stock]) * 100000000.  # 流通股本
    large_threshold = outstanding / 3600000

    tick_size = len(tick_day)
    for line in tick_day:
        cost_sum += line['price'] * line['volume']
        vol_sum += line['volume']
        if line['type'] == u'买盘':
            direction = 'a'
        elif line['type'] == u'卖盘':
            direction = 'd'
        if direction == 'a':
            tvi += line['volume']
            tmi += line['volume'] * line['price'] * 100
            if line['volume'] >= large_threshold:
                tvi_large += line['volume']
                tmi_large += line['volume'] * line['price'] * 100
                vol_buy_large_sum += line['volume']
            else:
                tvi_small += line['volume']
                tmi_small += line['volume'] * line['price'] * 100
                vol_buy_small_sum += line['volume']
        elif direction == 'd':
            tvi -= line['volume']
            tmi -= line['volume'] * line['price'] * 100
            if line['volume'] >= large_threshold:
                tvi_large -= line['volume']
                tmi_large -= line['volume'] * line['price'] * 100
                vol_sell_large_sum += line['volume']
            else:
                tvi_small -= line['volume']
                tmi_small -= line['volume'] * line['price'] * 100
                vol_sell_small_sum += line['volume']
    try:
        atpd = '%.2f' % (cost_sum / vol_sum)
    except ZeroDivisionError:
        return {'date': day, 'atpd': 0, 'vol_buy_large_sum': 0, 'vol_buy_small_sum': 0, 'vol_sell_large_sum': 0,
                'vol_sell_small_sum': 0, 'tvi': 0, 'tvi_large': 0, 'tmi': 0, 'tmi_large': 0, 'volume_sum': 0,
                'cost_sum': 0, 'tvi_small': 0, 'tmi_small': 0, 'tick_size': tick_size}
    return {'date': day, 'atpd': atpd, 'vol_buy_large_sum': vol_buy_large_sum, 'vol_buy_small_sum': vol_buy_small_sum,
            'vol_sell_large_sum': vol_sell_large_sum, 'vol_sell_small_sum': vol_sell_small_sum, 'tvi': tvi,
            'tvi_large': tvi_large, 'tvi_small': tvi_small, 'tmi': float('%.2f' % (tmi / 10000)),
            'tmi_large': float('%.2f' % (tmi_large / 10000)), 'tmi_small': float('%.2f' % (tmi_small / 10000)),
            'volume_sum': vol_sum, 'cost_sum': float('%.2f' % cost_sum), 'tick_size': tick_size}


# noinspection PyShadowingNames
def calc_average_trade_price_for_stock(idx):
    stock = data[idx]
    date_list = load_stock_date_list_from_tick_files(stock)
    global REFRESH_ATPD
    if REFRESH_ATPD:
        atpd_list = []
    else:
        atpd_list = load_atpd_data(stock)
    atpd_calced_date_list = [d['date'] for d in atpd_list]
    to_do_date_list = []
    for d in date_list:
        if d not in atpd_calced_date_list:
            to_do_date_list.append(d)
    if len(to_do_date_list) == 0:
        print('atpd for %s updated' % stock)
        return
    print('calc atpd for %s' % stock)
    for i in date_list:
        atpd_list.append(calc_average_trade_price_for_stock_one_day(stock, i))
    atpd_list_sorted = sorted(atpd_list, key=itemgetter('date'))
    b = pd.DataFrame(atpd_list_sorted)
    b = b.drop_duplicates('date', keep='last')
    b = b.reset_index()
    column_order = ['date', 'atpd', 'vol_buy_large_sum', 'vol_buy_small_sum', 'vol_sell_large_sum',
                    'vol_sell_small_sum', 'tvi', 'tvi_large', 'tvi_small', 'tmi', 'tmi_large', 'tmi_small',
                    'volume_sum',
                    'cost_sum', 'tick_size']
    b[column_order].to_csv('%s/quantitative_analysis/atpd/%s.csv' % (stock_data_root, stock), index=False)


if __name__ == '__main__':
    subprocess.call('mkdir -p %s/quantitative_analysis/atpd' % stock_data_root, shell=True)
    # FIXME buggy multi processing when re calculated
    results = list(futures.map(calc_average_trade_price_for_stock, range(len(data))))

    # pool = mp.Pool()
    # noinspection PyShadowingNames
    # for (idx, stock) in enumerate(BASIC_INFO.symbol_list):
    #    pool.apply_async(calc_average_trade_price_for_stock, args=(idx,))
    # pool.close()
    # pool.join()
