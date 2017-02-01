import csv
import os
import time
from operator import itemgetter

import tushare as ts
import pickle
from datetime import date, datetime, timedelta
import datetime

from variables import *


def get_today():
    from datetime import datetime
    ts = time.time()
    utc_now, now = datetime.utcfromtimestamp(ts), datetime.fromtimestamp(ts)
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(china_tz)
    return local_now.strftime("%Y-%m-%d")


def get_time():
    from datetime import datetime
    ts = time.time()
    utc_now, now = datetime.utcfromtimestamp(ts), datetime.fromtimestamp(ts)
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(china_tz)
    return local_now.strftime("%Y-%m-%d %H:%M:%S")


def get_time_of_a_day():
    from datetime import datetime
    ts = time.time()
    utc_now, now = datetime.utcfromtimestamp(ts), datetime.fromtimestamp(ts)
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(china_tz)
    return local_now.strftime("%H:%M:%S")


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


def get_weekends_of_a_year(year):
    d1 = date(int(year), 1, 1)
    d2 = date(int(year), 12, 31)
    days = []
    delta = d2 - d1
    from datetime import timedelta as td
    for i in range(delta.days + 1):
        if not check_weekday((d1 + td(days=i)).strftime('%Y-%m-%d')):
            days.append((d1 + td(days=i)).strftime('%Y-%m-%d'))
    return days


def create_market_close_days_for_year(year, other_close_dates_list):
    weekends_list = get_weekends_of_a_year(year)
    for d in other_close_dates_list:
        if d not in weekends_list:
            weekends_list.append(d)
    weekends_list.sort()
    with open('../stock_data/dates/market_close_days_%s.pickle' % year, 'wb') as f:
        pickle.dump(weekends_list, f)


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
    b = ts.get_h_data('000001', index=True, start=START_DATE)
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


def get_au_scaler_list_of_stock(stock):
    qfq = load_daily_data(stock)
    nonfq = load_daily_data(stock, autype='non_fq')
    result = {}
    for (price_qfq, price_non_fq) in zip(qfq, nonfq):
        result[price_qfq['date']] = price_qfq['close'] / price_non_fq['close']
    return result

def get_au_scaler_of_stock(stock, day):
    qfq = load_daily_data(stock)
    nonfq = load_daily_data(stock, autype='non_fq')
    price_qfq = 1
    price_non_fq = 1

    for line in qfq:
        if line['date'] == day:
            price_qfq = line['close']
            break
    for line in nonfq:
        if line['date'] == day:
            price_non_fq = line['close']
            break
    return price_qfq / price_non_fq


def load_tick_data(stock, day, autype='qfq', scaler=1):
    data_list = []
    with open('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, day)) as csvfile:
        reader = csv.DictReader(csvfile)
        try:
            for row in reader:
                row['price'] = float('%.2f' % (float(row['price']) * scaler))
                row['volume'] = int(row['volume'])
                row['amount'] = float(row['amount'])
                data_list.append(row)
        except:
            return []
    return data_list


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


def load_market_close_days_for_year(year):
    try:
        with open('../stock_data/dates/market_close_days_%s.pickle' % year, 'rb') as f:
            return pickle.load(f)
    except:
        return []


def load_ma_for_stock(stock, ma_params):
    try:
        with open("%s/qa/ma/%s/%s.pickle" % (stock_data_root, ma_params, stock), 'rb') as f:
            return pickle.load(f)
    except:
        return []


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


def load_daily_data(stock, autype='qfq'):
    data_list = []
    if autype == 'qfq':
        with open('../stock_data/data/%s.csv' % stock) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['open'] = float(row['open'])
                row['high'] = float(row['high'])
                row['close'] = float(row['close'])
                row['low'] = float(row['low'])
                row['volume'] = round(float(row['volume']))
                data_list.append(row)
    elif autype == 'non_fq':
        with open('../stock_data/data/%s_non_fq.csv' % stock) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['open'] = float(row['open'])
                row['high'] = float(row['high'])
                row['close'] = float(row['close'])
                row['low'] = float(row['low'])
                row['volume'] = round(float(row['volume']))
                data_list.append(row)
    data_new_sorted = sorted(data_list, key=itemgetter('date'))
    return data_new_sorted
