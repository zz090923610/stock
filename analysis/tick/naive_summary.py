# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED
import itertools
import multiprocessing as mp
import os

import pandas as pd

from tools.data.path_hdl import path_expand, directory_ensure
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import logging
from tools.data.mkt_chn.symbol_list_china_hdl import SymbolListHDL

# USEDIR( tick_quotes/china )
# REGDIR( naive_summary/china )
out_dir = path_expand("naive_summary/china")
directory_ensure(out_dir)
calendar = MktCalendar()


def generate_out_path_for(symbol):
    return os.path.join(out_dir, "%s.csv" % symbol)


def naive_summary_one_stock(symbol, date):
    data = pd.read_csv(os.path.join(path_expand("tick_quotes/china"), symbol, "%s.csv" % date))
    sub_data_buy = data[data['type'] == '买盘']
    sub_data_sell = data[data['type'] == '卖盘']
    sub_data_unknown = data[data['type'] == '中性盘']
    ave_price = data['amount'].sum() / data['volume'].sum() / 100
    quant_buy = sub_data_buy['volume'].sum()
    amount_buy = sub_data_buy['amount'].sum()

    quant_sell = sub_data_sell['volume'].sum()
    amount_sell = sub_data_sell['amount'].sum()

    quant_unknown = sub_data_unknown['volume'].sum()
    amount_unknown = sub_data_unknown['amount'].sum()

    new_row = [{'date': date, 'quant_buy': quant_buy, 'quant_sell': quant_sell, 'quant_unknown': quant_unknown,
                'amount_buy': amount_buy, 'amount_sell': amount_sell, 'amount_unknown': amount_unknown,
                'ave_price_tick': ave_price}]
    new_row_pd = pd.DataFrame(new_row).round(4)
    # noinspection PyBroadException,PyUnusedLocal
    try:
        ori_pd = pd.read_csv(generate_out_path_for(symbol))
        if date not in ori_pd['date'].tolist():
            ori_pd = pd.concat([ori_pd, new_row_pd], axis=0)
    except Exception as e:
        ori_pd = new_row_pd
    ori_pd = ori_pd.sort_values(by='date', ascending=True)
    col_order = ['date', 'quant_buy', 'quant_sell', 'quant_unknown', 'amount_buy', 'amount_sell', 'amount_unknown',
                 'ave_price_tick']
    ori_pd[col_order].to_csv(generate_out_path_for(symbol), index=False)
    logging("naive_summary", "finish %s %s" % (symbol, date))


def _naive_summary_one_stock_multiple_date(symbol, date_list):
    for (s, d) in itertools.product([symbol], date_list):
        try:
            naive_summary_one_stock(s, d)
        except Exception as e:
            logging("ERROR", "naive_summary %s" % e)


def naive_summary_multiple(symbol_list, date_list):
    pool = mp.Pool()
    for s in symbol_list:
        pool.apply_async(_naive_summary_one_stock_multiple_date, args=(s, date_list))
    pool.close()
    pool.join()


# CMDEXPORT ( NAIVETICKSUMMARY {date} ) naive_summary_tick
def naive_summary_tick(date):
    date_list = [calendar.parse_date(date)]
    symbol_list_hdl = SymbolListHDL()
    naive_summary_multiple(symbol_list_hdl.symbol_list, date_list)
