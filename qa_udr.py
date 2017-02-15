#!/usr/bin/python3
# -*- coding: utf-8 -*-


from common_func import *

import multiprocessing as mp


def calculate_udr_for_day(day):
    print('Calc UDR for day %s' % day)
    trade_data_for_day = []
    for stock in BASIC_INFO.symbol_list:
        daily_data = load_daily_data(stock)
        for line in daily_data:
            if day == line['date']:
                trade_data_for_day.append(line)

    advancing_volume = 0
    declining_volume = 0
    for line in trade_data_for_day:
        if (line['close'] - line['open']) > 0:
            advancing_volume += line['volume']
        elif (line['close'] - line['open']) < 0:
            declining_volume += line['volume']

    return {'date': day, 'advancing_volume': advancing_volume, 'declining_volume': declining_volume,
            'udr': advancing_volume / declining_volume}


def load_udr():
    data_list = []
    # noinspection PyBroadException
    try:
        with open('../stock_data/qa/udr.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['advancing_volume'] = round(float(row['advancing_volume']))
                row['declining_volume'] = round(float(row['declining_volume']))
                row['udr'] = float(row['udr'])
                data_list.append(row)
        data_new_sorted = sorted(data_list, key=itemgetter('date'))
        return data_new_sorted
    except:
        return []


def update_udr():
    market_open_date_list = load_market_open_date_list_from(START_DATE)
    udr = load_udr()
    udr_date_list = []
    for line in udr:
        udr_date_list.append(line['date'])

    to_do_list = []
    for day in market_open_date_list:
        if day not in udr_date_list:
            to_do_list.append(day)
    pool = mp.Pool()
    for i in to_do_list:
        pool.apply_async(calculate_udr_for_day, args=(i,), callback=udr.append)
    pool.close()
    pool.join()
    udr_sorted = sorted(udr, key=itemgetter('date'))
    b = pd.DataFrame(udr_sorted)
    column_order = ['date', 'advancing_volume', 'declining_volume', 'udr']
    b[column_order].to_csv('../stock_data/qa/udr.csv', index=False)


if __name__ == '__main__':
    update_udr()
