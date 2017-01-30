#!/usr/bin/python3
from qa_trend_continue import calc_average_trade_price_for_stock, calc_atpdr_for_stock
from qa_ma import ma_align
from qa_tick_lms import calc_lms_for_stocK_one_day_dict_wrap


def prepare_ma_lms_for_stock(stock, short, mid, long, refresh=False):
    calc_average_trade_price_for_stock(stock, refresh)
    calc_atpdr_for_stock(stock)
    m = ma_align(stock, short, mid, long)
    date_valid_list = m.date_valid
    ma_list = []
    for d in date_valid_list:
        r, o = m.analysis_align_for_day(d)
        r.update(calc_lms_for_stocK_one_day_dict_wrap(stock, d))
        ma_list.append(r)
    return ma_list, date_valid_list


def data_preparation():
    final_list = []
