#!/usr/bin/python3
# -*- coding: utf-8 -*-

from common_func import *


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
            # noinspection PyShadowingNames
            for i in range(0, n):
                denominator += abs(close_price_list[idx - i] - close_price_list[idx - i - 1])
            vhf = numerator / denominator
            data_for_day['vhf'] = vhf
    b = pd.DataFrame(daily_data)
    column_order = ['date', 'close', 'vhf']
    b[column_order].to_csv('../stock_data/qa/vhf/%s.csv' % stock, index=False)
    return daily_data


def calc_vhf_for_all_stock(n):
    # noinspection PyShadowingNames
    pool = mp.Pool()
    # noinspection PyShadowingNames
    for i in BASIC_INFO.symbol_list:
        pool.apply_async(calculate_vhf, args=(i, n))
    pool.close()
    pool.join()


def load_vhf_data(stock):
    data_list = []
    with open('../stock_data/qa/vhf/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['close'] = float(row['close'])
            if row['vhf'] == '-':
                continue
            row['vhf'] = float(row['vhf'])
            data_list.append(row)
    data_new_sorted = sorted(data_list, key=itemgetter('date'))
    return data_new_sorted


if __name__ == '__main__':
    pool = mp.Pool()
    for i in BASIC_INFO.symbol_list:
        pool.apply_async(calculate_vhf, args=(i, 5))
    pool.close()
    pool.join()
