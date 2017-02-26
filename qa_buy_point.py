#!/usr/bin/python3

import sys
from datetime import timedelta

from common_func import *
from variables import *


# noinspection PyShadowingNames
def save_buy_point_list_for_stock(stock, buy_point_list, buy_point_params):
    subprocess.call("mkdir -p %s/qa/buy_point/%s" % (stock_data_root, buy_point_params), shell=True)
    with open("%s/qa/buy_point/%s/%s.pickle" % (stock_data_root, buy_point_params, stock), 'wb') as f:
        pickle.dump(buy_point_list, f, -1)


# noinspection PyShadowingNames,PyUnusedLocal
def load_buy_point_list_for_stock(stock, buy_point_list, buy_point_params):
    # noinspection PyBroadException
    try:
        with open("%s/qa/buy_point/%s/%s.pickle" % (stock_data_root, buy_point_params, stock), 'rb') as f:
            return pickle.load(f)
    except:
        return []


# noinspection PyShadowingNames
def get_buy_point_for_stock(stock, pre_days, future_days, scale, retract=False):
    print("Finding buy point for %s" % stock)
    date_list = load_stock_date_list_from_daily_data(stock)
    date_list.sort()
    atpd_list = load_atpd_data(stock)
    buy_point_list = []
    assert len(date_list) == len(atpd_list)
    if (pre_days + future_days + 1) >= len(date_list):
        return []
    for day_idx in range(pre_days, len(date_list) - future_days):
        future_days_list = [date_list[i] for i in range(day_idx + 1, day_idx + future_days + 1)]
        future_days_data = [i for i in atpd_list if i['date'] in future_days_list]
        great_days_cnt = 0

        for line in future_days_data:
            if float(line['atpd']) / float(atpd_list[day_idx]['atpd']) >= float(scale):
                great_days_cnt += 1
        if great_days_cnt >= 2:
            buy_point_list.append(atpd_list[day_idx]['date'])
    r = ''
    if retract:
        buy_point_list = retract_buy_point_days(buy_point_list)
        r = 'r'
    save_buy_point_list_for_stock(stock, buy_point_list, '%d_%d_%.2f%s' % (pre_days, future_days, scale, r))
    return buy_point_list


def _check_two_days_next_to_each_other(day1, day2):
    date1 = datetime(int(day1.split('-')[0]), int(day1.split('-')[1]), int(day1.split('-')[2]), 1, 1, 1)
    date2 = date1 + timedelta(days=1)
    if day2 == date2.strftime("%Y-%m-%d"):
        return True
    else:
        return False


def retract_buy_point_days(day_list):
    if len(day_list) == 0:
        return []
    day_list.sort()
    day_to_remove = []
    for idx in range(len(day_list) - 1):
        if _check_two_days_next_to_each_other(day_list[idx], day_list[idx + 1]):
            day_to_remove.append(day_list[idx])
    for day in day_to_remove:
        day_list.remove(day)
    day_list.sort()
    return day_list


# noinspection PyShadowingNames
def get_buy_point_for_all_stock(pre_days, future_days, scale, retract=False):
    pool = mp.Pool()
    for i in BASIC_INFO.symbol_list:
        pool.apply_async(get_buy_point_for_stock, args=(i, pre_days, future_days, scale, retract))
    pool.close()
    pool.join()

if __name__ == '__main__':
    if len(sys.argv) == 0:
        exit()
    stock = None
    pre_days = None
    future_days = None
    scale = None
    retract = False
    for_all = False
    for loop in range(1, len(sys.argv)):
        if sys.argv[loop] == '--all':
            for_all = True
        elif sys.argv[loop] == '--stock':
            stock = sys.argv[loop + 1]
        elif sys.argv[loop] == '-p':
            pre_days = int(sys.argv[loop + 1])
        elif sys.argv[loop] == '-f':
            future_days = int(sys.argv[loop + 1])
        elif sys.argv[loop] == '--scale':
            scale = float(sys.argv[loop + 1])
        elif sys.argv[loop] == '-r':
            retract = True
    assert pre_days is not None
    assert future_days is not None
    assert scale is not None
    if for_all:
        get_buy_point_for_all_stock(pre_days, future_days, scale, retract=retract)
    else:
        buy_point_list = get_buy_point_for_stock(stock, pre_days, future_days, scale, retract=retract)
        print(buy_point_list)
