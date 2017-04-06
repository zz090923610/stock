import csv
import multiprocessing as mp
import os
import pickle
from operator import itemgetter

import pandas as pd

from stock.common.basic_stock_info_hdl import BasicInfoHDL
from stock.common.file_operation import logging
from stock.common.time_util import TimeUtil, str2date
from stock.common.variables import *

MARKET_OPEN_DATE_LIST = TimeUtil.load_historical_market_open_date_list()

BASIC_INFO = BasicInfoHDL()


def load_symbol_list(symbol_file):
    symbol_list = []
    if not os.path.isfile(symbol_file):
        BASIC_INFO.load()
    with open(symbol_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['timeToMarket'] != '0':
                symbol_list.append(row['code'])
    return symbol_list


# noinspection PyUnusedLocal
def get_au_scaler_list_of_stock(stock):
    # FIXME fix using yahoo
    # qfq = load_daily_data(stock)
    # nonfq = load_daily_data(stock, autype='non_fq')
    # result = {}
    # for (price_qfq, price_non_fq) in zip(qfq, nonfq):
    #    result[price_qfq['date']] = price_qfq['close'] / price_non_fq['close']
    return 1


def load_tick_data(stock, day):
    data_list = []
    with open('%s/tick_data/%s/%s_%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock, stock, day)) as csvfile:
        reader = csv.DictReader(csvfile)
        try:
            for row in reader:
                try:
                    row['price'] = float(row['price'])
                    row['volume'] = int(float(row['volume']))
                    row['amount'] = float(row['amount'])
                    data_list.append(row)
                except ValueError as e:
                    logging('%s %s' % (e, ('load_tick_data %s %s %s' % (stock, day, row['time']))))
        except FileNotFoundError:
            return []

    return data_list





def load_ma_for_stock(stock, ma_params):
    try:
        with open("%s/quantitative_analysis/ma/%s/%s.pickle" % (COMMON_VARS_OBJ.stock_data_root, ma_params, stock),
                  'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []


def load_trade_pause_date_list_for_stock(stock):
    try:
        with open('%s/trade_pause_date/%s.pickle' % (COMMON_VARS_OBJ.stock_data_root, stock), 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []


def load_basic_info_list():
    basic_info_list = []
    with open('%s/basic_info.csv' % COMMON_VARS_OBJ.stock_data_root) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            basic_info_list.append(row)
    basic_info_dict = {}
    for line in basic_info_list:
        basic_info_dict[line['code']] = line
    return basic_info_dict


BASIC_INFO_DICT = load_basic_info_list()


def print_basic_info(stock):
    basic_info = BASIC_INFO_DICT[stock]
    print('代码: {} 名称: {} 所属行业: {} 地区: {} \n\
市盈率: {} 流通股本(亿): {} 总股本(亿): {} 总资产(万): {} \n\
流动资产: {} 固定资产: {} 公积金: {} 每股公积金: {} 每股收益: {} \n\
每股净资: {} 市净率: {} 上市日期: {} 未分利润: {} 每股未分配: {}\n\
收入同比(%): {} 利润同比(%): {} 毛利率(%): {} 净利润率(%): {} 股东人数: {}'
          .format(basic_info['code'],
                  basic_info['name'],
                  basic_info['industry'],
                  basic_info['area'],
                  basic_info['pe'],
                  basic_info['outstanding'],
                  basic_info['totals'],
                  basic_info['totalAssets'],
                  basic_info['liquidAssets'],
                  basic_info['fixedAssets'],
                  basic_info['reserved'],
                  basic_info['reservedPerShare'],
                  basic_info['esp'],
                  basic_info['bvps'],
                  basic_info['pb'],
                  basic_info['timeToMarket'],
                  basic_info['undp'],
                  basic_info['perundp'],
                  basic_info['rev'],
                  basic_info['profit'],
                  basic_info['gpr'],
                  basic_info['npr'],
                  basic_info['holders']))


def save_trade_pause_date_date_list_for_stock(stock, pause_list):
    with open('%s/trade_pause_date/%s.pickle' % (COMMON_VARS_OBJ.stock_data_root, stock), 'wb') as f:
        pickle.dump(pause_list, f, -1)


def get_stock_open_date_list(stock_ipo_date):
    stock_date_list = []
    for day in MARKET_OPEN_DATE_LIST:
        if day >= stock_ipo_date:
            stock_date_list.append(day)
    return stock_date_list


def get_date_list(start, end, delta):
    curr = str2date(start)
    end = str2date(end)
    date_list = []
    while curr < end:
        date_list.append(curr.strftime("%Y-%m-%d"))
        curr += delta
    return date_list


def load_stock_date_list_from_daily_data(stock):
    date_list = []
    with open('%s/data/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date_list.append(row['date'])
    return date_list


def load_atpd_data(stock):
    """
    Average Trade Price daily.
    :param stock:
    :return:
    {'date': day, 'atpd': atpd, 'tvi': tvi, 'tvi_large': tvi_large, 'volume_sum': vol_sum,
            'cost_sum': float('%.2f' % cost_sum),
            'tick_size': tick_size}
    """
    data_list = []
    try:
        with open('%s/quantitative_analysis/atpd/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock)) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    row['atpd'] = float(row['atpd'])
                    row['tvi'] = int(float(row['tvi']))
                    row['tvi_large'] = int(float(row['tvi_large']))
                    row['volume_sum'] = int(float(row['volume_sum']))
                    row['cost_sum'] = float(row['cost_sum'])
                    row['tick_size'] = int(float(row['tick_size']))
                    data_list.append(row)
                except Exception as e:
                    print(e, row, stock)
        data_new_sorted = sorted(data_list, key=itemgetter('date'))
        return data_new_sorted
    except FileNotFoundError:
        return []


def load_daily_data(stock, autype='qfq'):
    data_list = []
    if autype == 'qfq':
        with open('%s/data/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock)) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['open'] = float(row['open'])
                row['high'] = float(row['high'])
                row['close'] = float(row['close'])
                row['low'] = float(row['low'])
                row['volume'] = round(float(row['volume']))
                data_list.append(row)
    elif autype == 'non_fq':
        with open('%s/data/%s_non_fq.csv' % (COMMON_VARS_OBJ.stock_data_root, stock)) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['open'] = float(row['open'])
                row['high'] = float(row['high'])
                row['close'] = float(row['close'])
                row['low'] = float(row['low'])
                row['volume'] = round(float(row['volume']))
                data_list.append(row)
    data_new_sorted = sorted(data_list, key=itemgetter('date'))
    return data_new_sorted


def generate_html(msg):
    html = """\
    <html>
      <head></head>
      <meta charset="UTF-8">
      <body>
        <p>
            %s
        </p>
      </body>
    </html>
    """ % msg
    return html


def load_stock_for_plot(stock, days):
    daily_data = pd.read_csv('%s/data/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock))
    daily_data = daily_data.sort_values(by='date', ascending=True)
    return daily_data.tail(days)


def load_atpdr_data(stock):
    """
    Average Trade Price daily.
    :param stock:
    :return:
    """
    data_list = []
    # noinspection PyBroadException
    try:
        with open('%s/quantitative_analysis/atpdr/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock)) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['cost_per_vol_1'] = float(row['cost_per_vol_1'])
                try:
                    row['cost_per_vol_3'] = float(row['cost_per_vol_3'])
                except ValueError:
                    row['cost_per_vol_3'] = None
                row['vol_per_tick_1'] = float(row['vol_per_tick_1'])
                try:
                    row['vol_per_tick_3'] = float(row['vol_per_tick_3'])
                except ValueError:
                    row['vol_per_tick_3'] = None
                row['atpd_ratio'] = float(row['atpd_ratio'])
                data_list.append(row)
        data_new_sorted = sorted(data_list, key=itemgetter('date'))
        return data_new_sorted
    except FileNotFoundError:
        return []


def load_stock_tick_data(stock, target_date):
    df = pd.read_csv('%s/tick_data/%s/%s_%s.csv' % (COMMON_VARS_OBJ.stock_data_root, stock, stock, target_date))
    df = df.sort_values(by='time', ascending=True)
    df = df.reset_index()
    df = df.drop('index', 1)
    # noinspection PyBroadException
    try:
        df = df.drop('Unnamed: 0', 1)
    except:
        pass
    return df
