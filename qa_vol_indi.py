#!/usr/bin/python3
import sys

from common_func import *
from qa_analysis_collect import AnalysisResult, add_analysis_result_one_stock_one_day
from variables import *

# data input: '../stock_data/qa/atpd/%s.csv' % stock
# data_input_type: csv
# data_input_column: []
# result_output: '../stock_data/qa/vol_indi/%s.csv' % stock
# result_output_format: csv
# result_output_column: ['date', 'vol_indi_large', 'vol_indi_small']

if not os.path.isdir('../stock_data/qa/vol_indi'):
    os.mkdir('../stock_data/qa/vol_indi', mode=0o777)


def calc_vol_indi_for_stock(stock):
    data_list = load_csv('../stock_data/qa/atpd/%s.csv' % stock,
                         col_type={'vol_buy_large_sum': 'int', 'vol_sell_large_sum': 'int',
                                   'vol_buy_small_sum': 'int', 'vol_sell_small_sum': 'int'})
    df = pd.DataFrame(data_list)
    if df.empty:
        return
    df['vol_sell_large_sum'] *= -1
    df['vol_sell_small_sum'] *= -1
    df['vol_buy_large_sum_0'] = df['vol_buy_large_sum'].shift(1)
    df['vol_sell_large_sum_0'] = df['vol_sell_large_sum'].shift(1)
    df['vol_buy_small_sum_0'] = df['vol_buy_small_sum'].shift(1)
    df['vol_sell_small_sum_0'] = df['vol_sell_small_sum'].shift(1)
    df['vol_indi_large'] = (df['vol_buy_large_sum'] - df['vol_buy_large_sum_0']) / \
                           (df['vol_sell_large_sum'] - df['vol_sell_large_sum_0'])
    df['vol_indi_small'] = (df['vol_buy_small_sum'] - df['vol_buy_small_sum_0']) / \
                           (df['vol_sell_small_sum'] - df['vol_sell_small_sum_0'])
    df = df.round({'vol_indi_small': 2, 'vol_indi_large': 2})
    df = df.fillna(0)
    df['buy_vol_indi'] = False
    for idx in df.loc[(df['vol_indi_small'] > 1) & (df['vol_indi_large'] > 1)].index:
        df.set_value(idx, 'buy_vol_indi', True)
    df[['date', 'vol_indi_large', 'vol_indi_small', 'buy_vol_indi']].to_csv('../stock_data/qa/vol_indi/%s.csv' % stock,
                                                                            index=False)
    for day in df.loc[(df['vol_indi_small'] > 1) & (df['vol_indi_large'] > 1)].date.tolist():
        add_analysis_result_one_stock_one_day(stock, day,
                                              'buy_vol_indi_%.2f_%.2f' % (
                                                  df[df['date'] == day]['vol_indi_large'].values[0],
                                                  df[df['date'] == day]['vol_indi_small'].values[0]))


def calc_vol_indi_for_all_stock():
    print('Calc VOL_INDI for all stock')
    # for i in BASIC_INFO.symbol_list:
    #    calc_vol_indi_for_stock(i)

    pool = mp.Pool()
    for i in BASIC_INFO.symbol_list:
        pool.apply_async(calc_vol_indi_for_stock, args=(i,))
    pool.close()
    pool.join()


def load_vol_indi_for_plot(stock, days):
    data = pd.read_csv('../stock_data/qa/vol_indi/%s.csv' % stock)
    data = data.sort_values(by='date', ascending=True)
    data = data.fillna(0)
    return data.tail(days)
