#!/usr/bin/python3
# -*- coding: utf-8 -*-
import csv
from _operator import itemgetter

import matplotlib
from matplotlib import ticker
from mpl_finance import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from common_func import BASIC_INFO
from variables import *
import pickle

from PIL import Image



def load_stock(stock, days):
    daily_data = pd.read_csv('../stock_data/data/%s.csv' % stock)
    daily_data = daily_data.sort_values(by='date', ascending=True)
    return daily_data.tail(days)


def load_ma_for_stock(stock, ma_params, days):
    try:
        with open("%s/qa/ma/%s/%s.pickle" % (stock_data_root, ma_params, stock), 'rb') as f:
            df = pd.DataFrame.from_dict(pickle.load(f), orient='columns', dtype=None)
    except FileNotFoundError:
        df = None
    df = df.sort_values(by='date', ascending=True)
    return df.tail(days)


def load_adl_for_stock(stock, days):
    data_list = []
    with open('../stock_data/qa/adl/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['open'] = float(row['open'])
            row['high'] = float(row['high'])
            row['close'] = float(row['close'])
            row['low'] = float(row['low'])
            row['adl'] = round(float(row['adl']))
            data_list.append(row)
    df = pd.DataFrame(data_list)
    df = df.sort_values(by='date', ascending=True)
    return df.tail(days)


def load_vhf_for_stock(stock, days):
    data_list = []
    with open('../stock_data/qa/vhf/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['close'] = float(row['close'])
            if row['vhf'] == '-':
                row['vhf'] = None
            else:
                row['vhf'] = float(row['vhf'])
            data_list.append(row)
    df = pd.DataFrame(data_list)
    df = df.sort_values(by='date', ascending=True)
    return df.tail(days)


def k_plot(stock, days, scale=False):
    if scale:
        fonts = [18, 20]
    else:
        fonts = [14, 16]
    s_full_name = BASIC_INFO.get_market_code_of_stock(stock)
    df = load_stock(stock, days)
    last_open = df.tail(1).iloc[-1]['open']
    last_close = df.tail(1).iloc[-1]['close']
    last_high = df.tail(1).iloc[-1]['high']
    last_low = df.tail(1).iloc[-1]['low']
    last_day_msg = ' 开:%.02f 收:%.02f 高:%.02f 低:%.02f' % (last_open, last_close, last_high, last_low)
    df_adl = load_adl_for_stock(stock, days)
    df_vhf = load_vhf_for_stock(stock, days)
    df_ma3 = load_ma_for_stock(stock, 'atpd_3', days)
    df_ma10 = load_ma_for_stock(stock, 'atpd_10', days)
    df_ma20 = load_ma_for_stock(stock, 'atpd_20', days)
    df_ma40 = load_ma_for_stock(stock, 'atpd_40', days)
    # plt.ion()
    fig = plt.figure(figsize=(16, 9), dpi=100)

    N = len(df.date)
    ind = np.arange(N)
    date_list = df['date'].tolist()

    def format_date(x, pos=None):
        thisind = np.clip(int(x + 0.5), 0, N - 1)
        return date_list[thisind]

    matplotlib.rcParams.update({'font.size': fonts[0]})
    ax1 = plt.subplot2grid((6, 1), (2, 0), rowspan=3)
    ax3 = plt.subplot2grid((6, 1), (5, 0), sharex=ax1)
    ax4 = plt.subplot2grid((6, 1), (1, 0), sharex=ax1)
    ax5 = plt.subplot2grid((6, 1), (0, 0), sharex=ax1)
    fig.suptitle(u'%s %s 日线图 %s %s' % (stock, BASIC_INFO.name_dict[stock], df_ma10['date'].tolist()[-1], last_day_msg),
                 fontsize=fonts[1])

    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    legend_list = []
    line_width = 1.5
    p_adl, = ax4.plot(ind, df_adl.adl, '-', label=u'累积/派发线(ADL)')
    plt.setp(p_adl, linewidth=2)
    leg4 = ax4.legend(handles=[p_adl], framealpha=0.3)

    p_vhf, = ax5.plot(ind, df_vhf.vhf, '-', label=u'盘整/趋势线(VHF)')
    plt.setp(p_vhf, linewidth=2)
    leg5 = ax5.legend(handles=[p_vhf], framealpha=0.3)


    p_ma3, = ax1.plot(ind, df_ma3.ma3, '-', label=u'MA3: %s' % df_ma3['ma3'].tolist()[-1])
    plt.setp(p_ma3, linewidth=line_width)
    legend_list.append(p_ma3)
    p_ma10, = ax1.plot(ind, df_ma10.ma10, '-', label=u'MA10: %s' % df_ma10['ma10'].tolist()[-1])
    plt.setp(p_ma10, linewidth=line_width)
    legend_list.append(p_ma10)
    p_ma20, = ax1.plot(ind, df_ma20.ma20, '-', label=u'MA20: %s' % df_ma20['ma20'].tolist()[-1])
    plt.setp(p_ma20, linewidth=line_width)
    legend_list.append(p_ma20)
    p_ma40, = ax1.plot(ind, df_ma40.ma40, '-', label=u'MA40: %s' % df_ma40['ma40'].tolist()[-1])
    plt.setp(p_ma40, linewidth=line_width)
    legend_list.append(p_ma40)
    leg = ax1.legend(handles=legend_list, )
    leg.get_frame().set_alpha(0.5)
    candlestick2_ochl(ax1, df.open, df.close, df.high, df.low, width=0.75, colorup='r', colordown='g', alpha=1)
    vc = volume_overlay(ax3, df.open, df.close, df.volume, colorup='r', colordown='g', width=1, alpha=1.0)
    ax3.add_collection(vc)
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(color='gray', linestyle='-')
    ax1.xaxis.grid(color='gray', linestyle='-')
    ax3.yaxis.grid(color='gray', linestyle='-')
    ax3.xaxis.grid(color='gray', linestyle='-')
    ax4.yaxis.grid(color='gray', linestyle='-')
    ax4.xaxis.grid(color='gray', linestyle='-')
    ax5.yaxis.grid(color='gray', linestyle='-')
    ax5.xaxis.grid(color='gray', linestyle='-')
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.subplots_adjust(top=0.92)
    fig.savefig('../stock_data/plots/%s.png' % s_full_name, transparent=True)
    if scale:
        fig.savefig('../stock_data/plots/%s.png' % s_full_name, transparent=True)
        cvt2gif(stock)
    plt.close()


def cvt2gif(stock):
    s_full_name = BASIC_INFO.get_market_code_of_stock(stock)
    img = Image.open('../stock_data/plots/%s.png' % s_full_name)
    img = img.resize((545, 300))
    img.save('../stock_data/plots/%s.png' % s_full_name, 'png')
