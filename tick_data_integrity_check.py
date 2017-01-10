#!/usr/bin/env python3

import os
import re
import sys
from multiprocessing import Pool
from time import sleep

import requests
from common_func import *
from get_tick_data import download_stock


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


def tick_data_content_check_one_stock_one_day(stock, day):
    data_list = []
    with open('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, day)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_list.append(row)
    if len(data_list) == 1:
        print("Repair %s %s" % (stock, day))
        os.remove('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, day))
        failed_list = load_fail_to_repair_list(stock)
        download_one_stock_one_day_from_qq(stock, day)
        failed_list.append(day)
        save_fail_to_repair_list(stock, failed_list)


def load_fail_to_repair_list(stock):
    try:
        with open('../stock_data/failed_downloaded_tick/%s.pickle' % stock, 'rb') as f:
            return pickle.load(f)
    except:
        return []


def save_fail_to_repair_list(stock, f_list):
    with open('../stock_data/failed_downloaded_tick/%s.pickle' % stock, 'wb') as f:
        pickle.dump(f_list, f, -1)


def check_one_stock_integrity(stock):
    failed_list = load_fail_to_repair_list(stock)
    daily_date_list = load_stock_date_list_from_daily_data(stock)
    tick_date_list = load_stock_date_list_from_tick_files(stock)
    for daily_day in daily_date_list:
        if daily_day in failed_list:
            continue
        if daily_day in tick_date_list:
            tick_data_content_check_one_stock_one_day(stock, daily_day)
            continue
        else:
            download_one_stock_one_day_from_qq(stock, daily_day)


def handle_check_one(stock):
    try:
        check_one_stock_integrity(stock)
    except:
        download_stock(stock)


def print_repaired_list():
    result_list = []
    file_list = os.listdir('../stock_data/failed_downloaded_tick')
    stock_list = []
    for f in file_list:
        stock_list.append(re.sub('.pickle$', '', f))
    for s in stock_list:
        date_list = load_fail_to_repair_list(s)
        for d in date_list:
            result_list.append('%s_%s' % (s, d))
    for r in result_list:
        print(r)
    print(len(result_list))


if __name__ == "__main__":
    if sys.argv[1] == '-p':
        print_repaired_list()
    else:
        p = Pool(8)
        rs = p.imap_unordered(handle_check_one, SYMBOL_LIST)
        p.close()  # No more work
        list_len = len(SYMBOL_LIST)
        while True:
            completed = rs._index
            if completed == list_len:
                break
            sys.stdout.write('%d/%d\r' % (completed, list_len))
            sys.stdout.flush()
            sleep(2)
        sys.stdout.write('Getting 1.000\n')
        sys.stdout.flush()
