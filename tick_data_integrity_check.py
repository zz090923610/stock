#!/usr/bin/env python3

import os
import sys
from multiprocessing import Pool
from time import sleep

import requests
from commom_func import *


def load_stock_date_list_from_tick_files(stock):
    file_list = os.listdir('../stock_data/tick_data/%s' % stock)
    if len(file_list) == 0:
        return None
    date_list = []
    for f in file_list:
        day = f.split('_')[1].split('.')[0]
        (y, m, d) = int(day.split('-')[0]), int(day.split('-')[1]), int(day.split('-')[2])
        date_list.append(datetime.datetime(y, m, d).strftime("%Y-%m-%d"))
    return date_list


def download_one_stock_one_day_from_qq(stock, a_day):
    print("Get %s %s" % (stock, a_day))
    s = requests.session()
    s.headers.update(AGENT)
    hb_params = dict(
        appn='detail',
        action='download',
        c='sz%s' % stock,
        d='%s' % a_day.replace('-', ''),
    )
    txtdata = s.get('http://stock.gtimg.cn/data/index.php', params=hb_params)
    if txtdata.content == b'\xd4\xdd\xce\xde\xca\xfd\xbe\xdd':
        hb_params = dict(
            appn='detail',
            action='download',
            c='sh%s' % stock,
            d='%s' % a_day.replace('-', ''),
        )
        txtdata = s.get('http://stock.gtimg.cn/data/index.php', params=hb_params)
    final_data = txtdata.content.decode('gbk').replace('\t', ',')
    final_data = final_data.replace('成交时间', 'time')
    final_data = final_data.replace('成交价格', 'price')
    final_data = final_data.replace('价格变动', 'change')
    final_data = final_data.replace('成交量(手)', 'volume')
    final_data = final_data.replace('成交额(元)', 'amount')
    final_data = final_data.replace('性质', 'type')
    with open('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, a_day), 'wb') as mytextfile:
        mytextfile.write(final_data.encode('utf8'))
    qq_csv_format_correction('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, a_day))


def qq_csv_format_correction(csv_file):
    a = [['time', 'price', 'change', 'volume', 'amount', 'type']]
    with open(csv_file) as f:
        for row in reversed(list(csv.reader(f))):
            if row != ['time', 'price', 'change', 'volume', 'amount', 'type']:
                a.append(row)
    for (idx, row) in enumerate(a):
        if idx == 0:
            row.insert(0, '')
        else:
            row.insert(0, idx - 1)
    with open(csv_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(a)


def check_one_stock_integrity(stock):
    daily_date_list = load_stock_date_list_from_daily_data(stock)
    tick_date_list = load_stock_date_list_from_tick_files(stock)
    for daily_day in daily_date_list:
        if daily_day in tick_date_list:
            continue
        else:
            download_one_stock_one_day_from_qq(stock, daily_day)


if __name__ == "__main__":
    p = Pool(64)
    rs = p.imap_unordered(check_one_stock_integrity, SYMBOL_LIST)
    p.close()  # No more work
    list_len = len(SYMBOL_LIST)
    while True:
        completed = rs._index
        if completed == list_len:
            break
        sys.stdout.write('Getting %.3f\n' % (completed / list_len))
        sys.stdout.flush()
        sleep(2)
    sys.stdout.write('Getting 1.000\n')
    sys.stdout.flush()
    # for stock in SYMBOL_LIST:
    #    check_one_stock_integrity(stock)
