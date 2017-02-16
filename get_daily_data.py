#!/usr/bin/python3
import sys
from io import StringIO
from multiprocessing import Pool

from common_func import *

TODAY = get_today()


def get_daily_data_for_stock_yahoo(stock, start_day, end_day):
    column_order = ['date', 'open', 'high', 'close', 'low', 'volume']
    try:
        df_already = pd.read_csv('../stock_data/data/%s.csv' % stock)
    except FileNotFoundError:
        df_already = pd.DataFrame(columns=['date', 'open', 'high', 'close', 'low', 'volume'])
    if start_day == end_day:
        if end_day in df_already.date.unique():
            df_already = df_already.drop_duplicates('date', keep='last')
            df_already[column_order].to_csv('../stock_data/data/%s.csv' % stock, index=False)
            return
    s = requests.session()
    start_year, start_month, s_day = int(start_day.split('-')[0]), int(start_day.split('-')[1]) - 1, int(
        start_day.split('-')[2])
    end_year, end_month, e_day = int(end_day.split('-')[0]), int(end_day.split('-')[1]) - 1, int(
        end_day.split('-')[2])
    req_url = 'http://chart.finance.yahoo.com/table.csv'
    get_headers = {'User-Agent': AGENT['User-Agent']}
    if BASIC_INFO.market_dict[stock] == 'sse':
        market = 'SS'
    else:
        market = 'SZ'
    get_params = {'s': '%s.%s' % (stock, market),
                  'a': start_month,
                  'b': s_day,
                  'c': start_year,
                  'd': end_month,
                  'e': e_day,
                  'f': end_year,
                  'g': 'd',
                  'ignore': '.csv'}
    result = s.get(req_url, headers=get_headers, params=get_params)
    if result.status_code == 404:
        logging('get_daily_data_for_stock_yahoo %s %s %s not fount on yahoo' % (stock, start_day, end_day))
        df = ts.get_k_data(stock, start=start_day, end=end_day)
        df = df.sort_values(by='date', ascending=True)
        df[column_order].to_csv('../stock_data/data/%s.csv' % stock, index=False)
    elif result == 200:
        csv_data = result.text
        csv_data = csv_data.lower()
        df = pd.read_csv(StringIO(csv_data))
        df.volume /= 100

        if (len(df.date) == 1) & (start_day == end_day):
            df = df_already.append(df, ignore_index=True)

        df = df[df.volume != 0]
        if e_day not in df_already.date.unique():
            tmp_data = ts.get_k_data(stock)
            df = df.append(tmp_data, ignore_index=True)
        df.volume = df.volume.astype(int)
        df = df.sort_values(by='date', ascending=True)
        df = df.loc[df['date'].isin(BASIC_INFO.market_open_days)]
        df = df.round({'open': 2, 'high': 2, 'close': 2, 'low': 2})
        df = df.drop_duplicates('date', keep='last')
        df[column_order].to_csv('../stock_data/data/%s.csv' % stock, index=False)


def get_daily_data_for_all_stock_range_yahoo(start_day, end_day):
    pool = mp.Pool(64)
    for stock in BASIC_INFO.symbol_list:
        pool.apply_async(get_daily_data_for_stock_yahoo, args=(stock, start_day, end_day,))
    pool.close()
    pool.join()


def get_update_for_all_stock():
    pool = mp.Pool()
    for stock in BASIC_INFO.symbol_list:
        pool.apply_async(get_daily_data_for_stock_yahoo, args=(stock, TODAY, TODAY))
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
        print('Getting All daily Data For All Stock')
        get_daily_data_for_all_stock_range_yahoo(START_DATE, TODAY)
    elif fetch_type == 'update':
        get_update_for_all_stock()
