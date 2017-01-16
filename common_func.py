import csv
import os
import time

import pytz
import tushare as ts
import pickle
from datetime import date, datetime, timedelta
import datetime

from tzlocal import get_localzone

START_DATE = '2012-01-01'
# get local timezone
local_tz = get_localzone()
china_tz = pytz.timezone('Asia/Shanghai')
AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
POOL_SIZE = 128


def get_today():
    return time.strftime("%Y-%m-%d")


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


def check_weekday(date_str):
    (y, m, d) = int(date_str.split('-')[0]), int(date_str.split('-')[1]), int(date_str.split('-')[2])
    if datetime.datetime(y, m, d).weekday() in range(0, 5):
        return True
    else:
        return False


def update_basic_info():
    bi = ts.get_stock_basics()
    bi.to_csv('../stock_data/basic_info.csv')


def str2date(str_date):
    (y, m, d) = int(str_date.split('-')[0]), int(str_date.split('-')[1]), int(str_date.split('-')[2])
    return date(y, m, d)


def load_time_to_market_list():
    symbol_dict = {}
    if not os.path.isfile('../stock_data/basic_info.csv'):
        update_basic_info()
    with open('../stock_data/basic_info.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            (y, m, d) = row['timeToMarket'][0:4], row['timeToMarket'][4:6], row['timeToMarket'][6:8]
            symbol_dict[row['code']] = '%s-%s-%s' % (y, m, d)
    return symbol_dict


IPO_DATE_LIST = load_time_to_market_list()


def load_symbol_list(symbol_file):
    symbol_list = []
    if not os.path.isfile(symbol_file):
        update_basic_info()
    with open(symbol_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['timeToMarket'] != '0':
                symbol_list.append(row['code'])
    return symbol_list


SYMBOL_LIST = load_symbol_list('../stock_data/basic_info.csv')


def update_market_open_date_list():
    b = ts.get_h_data('000001', index=True, start='2008-01-01')
    days_cnt = len(b.index)
    days_list = []
    for idx in range(0, days_cnt):
        days_list.append(b.iloc[idx].name.strftime('%Y-%m-%d'))
    save_market_open_date_list(days_list)
    return days_list


def load_market_open_date_list():
    try:
        with open('../stock_data/market_open_date_list.pickle', 'rb') as f:
            return pickle.load(f)
    except:
        return update_market_open_date_list()

def load_market_open_date_list_from(given_day):
    try:
        with open('../stock_data/market_open_date_list.pickle', 'rb') as f:
            raw_date = pickle.load(f)
    except:
        raw_date = update_market_open_date_list()
    result_list = []
    for day in raw_date:
        if day >= given_day:
            result_list.append(day)
    return result_list


def save_market_open_date_list(market_open_date_list):
    with open('../stock_data/market_open_date_list.pickle', 'wb') as f:
        pickle.dump(market_open_date_list, f, -1)


MARKET_OPEN_DATE_LIST = load_market_open_date_list()


def load_trade_pause_date_list_for_stock(stock):
    try:
        with open('../stock_data/trade_pause_date/%s.pickle' % stock, 'rb') as f:
            return pickle.load(f)
    except:
        return []


def save_trade_pause_date_date_list_for_stock(stock, pause_list):
    with open('../stock_data/trade_pause_date/%s.pickle' % stock, 'wb') as f:
        pickle.dump(pause_list, f, -1)


def get_stock_open_date_list(stock_ipo_date):
    stock_date_list = []
    for day in MARKET_OPEN_DATE_LIST:
        if day >= stock_ipo_date:
            stock_date_list.append(day)
    return stock_date_list


def get_date_list(start, end, delta):
    curr = str2date(start)
    end = str2date(end)
    date_list = []
    while curr < end:
        date_list.append(curr.strftime("%Y-%m-%d"))
        curr += delta
    return date_list


def load_stock_date_list_from_daily_data(stock):
    date_list = []
    with open('../stock_data/data/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date_list.append(row['date'])
    return date_list


def mkdirs(symbol_list):
    try:
        if not os.path.isdir('../stock_data/tick_data'):
            os.mkdir('../stock_data/tick_data', mode=0o777)
        for s_code in symbol_list:
            if not os.path.isdir('../stock_data/tick_data/%s' % s_code):
                os.mkdir('../stock_data/tick_data/%s' % s_code, mode=0o777)
    except KeyboardInterrupt:
        exit(0)
    except:
        pass
