#!/usr/bin/python3
# -*- coding: utf-8 -*-

from stock.common.common_func import *


def load_adl_data(stock):
    data_list = []
    with open('%s/quantitative_analysis/adl/%s.csv' % (stock_data_root, stock)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['open'] = float(row['open'])
            row['high'] = float(row['high'])
            row['close'] = float(row['close'])
            row['low'] = float(row['low'])
            row['adl'] = round(float(row['adl']))
            data_list.append(row)
    data_new_sorted = sorted(data_list, key=itemgetter('date'))
    return data_new_sorted


def calculate_adl_for_stock(stock):
    subprocess.call("mkdir -p %s/quantitative_analysis/adl" % stock_data_root, shell=True)
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
        # noinspection PyUnboundLocalVariable
        item = round(item)
        if idx == 0:
            line['adl'] = item
        else:
            line['adl'] = item + daily_data[idx - 1]['adl']
    daily_data_sorted = sorted(daily_data, key=itemgetter('date'))
    b = pd.DataFrame(daily_data_sorted)
    column_order = ['date', 'open', 'high', 'close', 'low', 'adl']
    b[column_order].to_csv('%s/quantitative_analysis/adl/%s.csv' % (stock_data_root, stock), index=False)
    return daily_data_sorted


def calc_adl_for_all_stock():
    pool = mp.Pool()
    for i in BASIC_INFO.symbol_list:
        pool.apply_async(calculate_adl_for_stock, args=(i,))
    pool.close()
    pool.join()


if __name__ == '__main__':
    calc_adl_for_all_stock()
