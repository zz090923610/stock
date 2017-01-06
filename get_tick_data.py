#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from commom_func import *

def download_stock(s_code):
    finished = False
    while not finished:
        current_file_date = get_lastest_date(s_code)
        start = max(IPO_DATE_LIST[s_code], '2008-01-01')

        if current_file_date is not None:
            start = current_file_date
        date_list = get_date_list(start, get_today(), timedelta(days=1))
        try:
            for a_day in date_list:
                _download_one_stock_one_day(s_code, a_day)
            finished = True
        except KeyboardInterrupt:
            exit(0)
        except:
            finished = False


def mkdirs(symbol_list):
    try:
        os.mkdir('../stock_data/tick_data', mode=0o777)
        for s_code in symbol_list:
            os.mkdir('../stock_data/tick_data/%s' % s_code, mode=0o777)
    except KeyboardInterrupt:
        exit(0)
    except:
        pass


def _download_one_stock_one_day(scode, a_day):
    if Path('../stock_data/tick_data/%s/%s_%s.csv' % (scode, scode, a_day)).is_file():
        print('Exist %s %s' % (scode, a_day), file=sys.stderr)
        return
    print("Get %s %s" % (scode, a_day))
    data = ts.get_tick_data(scode, date=a_day)
    try:
        if data.iloc[0]['time'].find("当天没有数据") == -1:
            data.to_csv('../stock_data/tick_data/%s/%s_%s.csv' % (scode, scode, a_day))
    except KeyboardInterrupt:
        exit(0)
    except:
        print('ERROR Get %s %s' % (scode, a_day), file=sys.stderr)


def get_lastest_date(s_code):
    file_list = os.listdir('../stock_data/tick_data/%s' % s_code)
    if len(file_list) == 0:
        return None
    date_list = []
    for f in file_list:
        day = f.split('_')[1].split('.')[0]
        (y, m, d) = int(day.split('-')[0]), int(day.split('-')[1]), int(day.split('-')[2])
        date_list.append(datetime.datetime(y, m, d))
    return max(date_list).strftime("%Y-%m-%d")


def load_finished_stock_list(group):
    try:
        with open('../stock_data/finished_group_%s.pickle' % group, 'rb') as f:
            return pickle.load(f)
    except:
        return []


def save_finished_stock_list(f_s_list, group):
    with open('../stock_data/finished_group_%s.pickle' % group, 'wb') as f:
        pickle.dump(f_s_list, f, -1)


if __name__ == "__main__":
    group = sys.argv[1]
    finished_stock_list = load_finished_stock_list(group)
    symbol_list_group = load_symbol_list('../stock_data/basic_info_%s.csv' % group)
    for stock in symbol_list_group:
        if stock in finished_stock_list:
            continue
        download_stock(stock)
        finished_stock_list.append(stock)
        save_finished_stock_list(finished_stock_list, group)