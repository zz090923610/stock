#!/usr/bin/env python3
import sys
# noinspection PyCompatibility
from pathlib import Path

from datetime import timedelta

from stock.common.common_func import *
from stock.quantitative_analysis.qa_tick_lms import calculate_lms_for_stock_one_day, load_tick_data
TODAY =get_today()

# noinspection PyShadowingNames
def load_fail_to_repair_list(stock: str):
    """

    :type stock: str
    """
    try:
        with open('%s/failed_downloaded_tick/%s.pickle' % (stock_data_root, stock), 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []


# noinspection PyShadowingNames
def load_something_for_stock_one_day(stock, day, something):
    volume = 0
    with open('%s/data/%s.csv' % (stock_data_root, stock)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['date'] == day:
                volume = float(row[something])
    return volume


def download_stock(s_code):
    finished = False
    while not finished:
        current_file_date = get_last_date(s_code)
        df_already = pd.read_csv('%s/data/%s.csv' % (stock_data_root, stock))
        date_list = df_already['date'].tolist()
        if current_file_date is not None:
            start = current_file_date
        date_list = [day for day in date_list if day >= start]
        # noinspection PyBroadException
        try:
            for a_day in date_list:
                _download_one_stock_one_day("%s+%s" % (s_code, a_day))
            finished = True
        except KeyboardInterrupt:
            exit(0)
        except:
            finished = False


def generate_day_list_for_stock(s_code):
    failed_loaded_list = load_fail_to_repair_list(s_code)
    current_file_date = get_last_date(s_code)
    start = max(BASIC_INFO.time_to_market_dict[s_code], START_DATE)
    all_date_list = get_stock_open_date_list(start)
    if current_file_date is None:
        return all_date_list
    date_list = []
    for day in all_date_list:
        if day in failed_loaded_list:
            continue
        if day >= current_file_date:
            date_list.append(day)
    return date_list


def generate_work_list(s_code, date_list):
    result = []
    for day in date_list:
        result.append('%s+%s' % (s_code, day))
    return result


# noinspection PyBroadException
def _download_one_stock_one_day(scode_a_day):
    (scode, a_day) = scode_a_day.split('+')[0], scode_a_day.split('+')[1]
    if Path('%s/tick_data/%s/%s_%s.csv' % (stock_data_root, scode, scode, a_day)).is_file():
        print('Exist %s %s' % (scode, a_day), file=sys.stderr)
        return
    print("Get %s %s" % (scode, a_day))
    try:
        data = ts.get_tick_data(scode, date=a_day)
    except:
        return
    try:
        if data.iloc[0]['time'].find("当天没有数据") == -1:
            data.to_csv('%s/tick_data/%s/%s_%s.csv' % (stock_data_root, scode, scode, a_day))
    except KeyboardInterrupt:
        exit(0)
    except:
        print('ERROR Get %s %s' % (scode, a_day), file=sys.stderr)


def get_last_date(s_code):
    file_list = os.listdir('%s/tick_data/%s' % (stock_data_root, s_code))
    if len(file_list) == 0:
        return None
    date_list = []
    for f in file_list:
        day = f.split('_')[1].split('.')[0]
        (y, m, d) = int(day.split('-')[0]), int(day.split('-')[1]), int(day.split('-')[2])
        date_list.append(datetime(y, m, d))
    return max(date_list).strftime("%Y-%m-%d")


# noinspection PyShadowingNames
def align_tick_data_stock(stock):
    daily_date_list = load_stock_date_list_from_daily_data(stock)
    tick_date_list = load_stock_date_list_from_tick_files(stock)
    for (idx, day) in enumerate(daily_date_list):
        if day not in tick_date_list:
            if idx > 0:

                _download_one_stock_one_day('%s+%s' % (stock, day))
                if os.path.isfile('%s/tick_data/%s/%s_%s.csv' % (stock_data_root, stock, stock, day)):
                    continue
                print('Still missing tick data for %s %s' % (stock, day))
                (buy_large, sell_large, buy_mid, sell_mid, buy_small, sell_small,
                 undirected_trade) = calculate_lms_for_stock_one_day(stock, daily_date_list[idx - 1])
                yesterday_volume = buy_large + sell_large + buy_mid + sell_mid + buy_small + sell_small + \
                    undirected_trade
                today_volume = load_something_for_stock_one_day(stock, day, 'volume')
                today_price = load_something_for_stock_one_day(stock, day, 'close')
                yesterday_tick = load_tick_data(stock, daily_date_list[idx - 1])
                for row in yesterday_tick:
                    row['price'] = today_price
                    row['volume'] = round(row['volume'] * (yesterday_volume / today_volume))
                    row['amount'] = round(row['price'] * row['volume'] * 100)
                yesterday_tick.append(
                    {'': len(yesterday_tick), 'time': '08:00:00', 'price': today_price, 'change': 0, 'volume': 0,
                     'amount': 0, 'type': '买盘'})
                b = pd.DataFrame(yesterday_tick)
                column_order = ['time', 'price', 'change', 'volume', 'amount', 'type']
                b[column_order].to_csv('%s/tick_data/%s/%s_%s.csv' % (stock_data_root, stock, stock, day))


if __name__ == "__main__":
    all_work_list = []
    if sys.argv[1] == '--day':
        target_day = sys.argv[2]
        for stock in BASIC_INFO.symbol_list:
            day_list = [target_day]
            all_work_list += generate_work_list(stock, day_list)
    elif sys.argv[1] == '--align':
        pool = mp.Pool()
        for stock in BASIC_INFO.symbol_list:
            pool.apply_async(align_tick_data_stock, args=(stock,))
        pool.close()
        pool.join()
        exit()
    else:
        for stock in BASIC_INFO.symbol_list:
            day_list = generate_day_list_for_stock(stock)
            all_work_list += generate_work_list(stock, day_list)

    pool = mp.Pool(64)
    for stock in all_work_list:
        pool.apply_async(_download_one_stock_one_day, args=(stock,))
    pool.close()
    pool.join()
