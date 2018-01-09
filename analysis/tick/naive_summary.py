import os

import itertools
import pandas as pd
import multiprocessing as mp

from configs.path import DIRs
from tools.io import logging
from tools.symbol_list_china_hdl import SymbolListHDL


def generate_input_path(symbol, date):
    return os.path.join(DIRs['TICK_QUOTES_CHINA'], symbol, "%s.csv" % date)


def generate_out_path(symbol):
    return os.path.join(DIRs['DATA_ROOT'], "naive_summary", "china", "%s.csv" % symbol)


def naive_summary_one_stock(symbol, date):
    data = pd.read_csv(generate_input_path(symbol, date))
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
    try:
        ori_pd = pd.read_csv(generate_out_path(symbol))
        if date not in ori_pd['date'].tolist():
            ori_pd = pd.concat([ori_pd, new_row_pd], axis=0)
    except Exception as e:
        ori_pd = new_row_pd
    ori_pd = ori_pd.sort_values(by='date', ascending=True)

    ori_pd.to_csv(generate_out_path(symbol), index=False)
    logging("naive_summary", "finish %s %s"% (symbol, date))


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


def naive_summary_all(date_list):
    symbol_list_hdl = SymbolListHDL()
    naive_summary_multiple(symbol_list_hdl.symbol_list, date_list)
