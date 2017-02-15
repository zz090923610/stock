#!/usr/bin/python3
import sys
from io import StringIO
from multiprocessing import Pool

from common_func import *


def get_daily_data_for_stock_one_day_yahoo(stock, day):
    get_daily_data_for_stock_yahoo(stock, day, day)


def get_daily_data_for_stock_yahoo(stock, start_day, end_day):
    try:
        df_already = pd.read_csv('../stock_data/data/%s.csv' % stock)
    except FileNotFoundError:
        df_already = pd.DataFrame(columns=['date', 'open', 'high', 'close', 'low', 'volume'])
    if start_day == end_day:
        if start_day in df_already.date.unique():
            return
    s = requests.session()
    start_year, start_month, start_day = int(start_day.split('-')[0]), int(start_day.split('-')[1]) - 1, int(
        start_day.split('-')[2])
    end_year, end_month, end_day = int(end_day.split('-')[0]), int(end_day.split('-')[1]) - 1, int(
        end_day.split('-')[2])
    print('Get %s daily data from yahoo' % stock)
    req_url = 'http://chart.finance.yahoo.com/table.csv'
    get_headers = {'User-Agent': AGENT['User-Agent']}
    if BASIC_INFO.market_dict[stock] == 'sse':
        market = 'SS'
    else:
        market = 'SZ'
    get_params = {'s': '%s.%s' % (stock, market),
                  'a': start_month,
                  'b': start_day,
                  'c': start_year,
                  'd': end_month,
                  'e': end_day,
                  'f': end_year,
                  'g': 'd',
                  'ignore': '.csv'}
    result = s.get(req_url, headers=get_headers, params=get_params)
    csv_data = result.text
    csv_data = csv_data.lower()
    df = pd.read_csv(StringIO(csv_data))
    df.volume /= 100
    df.volume = df.volume.astype(int)
    if (len(df.date) == 1) & (start_day == end_day):
        df = df_already.append(df, ignore_index=True)
    column_order = ['date', 'open', 'high', 'close', 'low', 'volume']
    df = df[df.volume != 0]
    df = df.sort_values(by='date', ascending=True)
    df[column_order].to_csv('../stock_data/data/%s.csv' % stock, index=False)


def get_daily_data_for_all_stock_one_day_yahoo(day):
    pool = mp.Pool()
    for stock in BASIC_INFO.symbol_list:
        pool.apply_async(get_daily_data_for_stock_one_day_yahoo, args=(stock, day,))
    pool.close()
    pool.join()


def get_daily_data_for_all_stock_range_yahoo(start_day, end_day):
    pool = mp.Pool()
    for stock in BASIC_INFO.symbol_list:
        pool.apply_async(get_daily_data_for_stock_yahoo, args=(stock, start_day, end_day,))
    pool.close()
    pool.join()


def get_all_data_for_one_stock(stock):
    get_daily_data_for_stock_yahoo(stock, START_DATE, get_today())
    # print('getting %s' % stock)
    # start = max(BASIC_INFO.time_to_market_dict[stock], START_DATE)
    # my_file = Path('../stock_data/data/%s.csv' % stock)
    # if my_file.is_file():
    #    get_update_for_one_stock(stock)
    #    return
    # data = ts.get_k_data(stock, autype='qfq', start=start, end=get_today())
    # data = data.reindex(index=data.index[::-1])
    # cols = ['date', 'open', 'high', 'close', 'low', 'volume']
    # data[cols].to_csv('../stock_data/data/%s.csv' % stock, index=False)
    # data_non_fq = ts.get_k_data(stock, autype='None', start=start, end=get_today())
    # data_non_fq = data_non_fq.reindex(index=data.index[::-1])
    # data_non_fq[cols].to_csv('../stock_data/data/%s_non_fq.csv' % stock, index=False)


def get_all_data_for_all_stock():
    get_daily_data_for_all_stock_range_yahoo(START_DATE, get_today())
    # p = Pool(64)
    # rs = p.imap_unordered(get_all_data_for_one_stock, BASIC_INFO.symbol_list)
    # p.close()  # No more work
    # list_len = len(BASIC_INFO.symbol_list)
    # while True:
    #    completed = rs._index
    #    if completed == list_len:
    #        break
    #    sys.stdout.write('Getting %.3f\n' % (completed / list_len))
    #    sys.stdout.flush()
    #    sleep(2)
    # sys.stdout.write('Getting 1.000\n')
    # sys.stdout.flush()


def get_update_for_one_stock(stock):
    get_daily_data_for_stock_one_day_yahoo(stock, get_today())


def get_update_for_all_stock():
    pool = mp.Pool()
    for stock in BASIC_INFO.symbol_list:
        pool.apply_async(get_update_for_one_stock, args=(stock,))
    pool.close()
    pool.join()


if __name__ == "__main__":
    fetch_type = 'all'
    for loop in range(1, len(sys.argv)):
        if sys.argv[loop] == '--all':
            fetch_type = 'all'
        elif sys.argv[loop] == '--update':
            fetch_type = 'update'
    if fetch_type == 'all':
        get_all_data_for_all_stock()
    elif fetch_type == 'update':
        get_update_for_all_stock()
