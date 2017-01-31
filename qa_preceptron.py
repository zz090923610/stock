#!/usr/bin/python3
from qa_trend_continue import calc_average_trade_price_for_stock, calc_atpdr_for_stock, calc_atpd_for_all_stock
from qa_ma import ma_align
from qa_tick_lms import calc_lms_for_stocK_one_day_dict_wrap
from qa_adl import calculate_adl_for_stock
from qa_vhf import calculate_vhf
from qa_buy_point import get_buy_point_for_stock
from common_func import *
import multiprocessing as mp
import pandas as pd


def prepare_ma_lms_adl_for_stock(stock, short, mid, long, refresh=False, vhf_n=5):
    calc_average_trade_price_for_stock(stock, refresh)
    calc_atpdr_for_stock(stock)
    adl = calculate_adl_for_stock(stock)
    vhf = calculate_vhf(stock, vhf_n)
    buy_point_list = get_buy_point_for_stock(stock, 10, 30, 1.2)
    m = ma_align(stock, short, mid, long)
    date_valid_list = m.date_valid
    ma_list = []
    for d in date_valid_list:
        r, o = m.analysis_align_for_day(d)
        r.update(calc_lms_for_stocK_one_day_dict_wrap(stock, d))
        for l in adl:
            if l['date'] == d:
                r['adl'] = l['adl']
                break
        for l in vhf:
            if l['date'] == d:
                r['vhf'] = l['vhf']
                break
        if d in buy_point_list:
            r['buy_point'] = True
        else:
            r['buy_point'] = False
        r['stock'] = stock
        ma_list.append(r)
    return ma_list


def data_preparation():
    final_list = []
    calc_atpd_for_all_stock()
    pool = mp.Pool()
    for i in SYMBOL_LIST:
        pool.apply_async(prepare_ma_lms_adl_for_stock, args=(i, 10, 20, 40), callback=final_list.append)
    pool.close()
    pool.join()
    b = pd.DataFrame(final_list)
    b.to_csv('../stock_data/qa/preceptron.csv', index=False)
    return final_list

if __name__ == '__main__':
    data_preparation()
