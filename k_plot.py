#!/usr/bin/python3
# -*- coding: utf-8 -*-
import csv
import pickle
import subprocess

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from matplotlib import ticker
from mpl_finance import *

from common_func import BASIC_INFO, logging
from qa_linear_fit import get_fitted_data
from variables import *
from intraday_plot import intraday_plot


def calc_tmi_series_for_stock(stock, days):
    print('Calc TMI for %s' % stock)
    atpd_data = pd.read_csv('../stock_data/qa/atpd/%s.csv' % stock)
    atpd_data = atpd_data.sort_values(by='date', ascending=True)
    atpd_data = atpd_data.tail(days)
    atpd_data = atpd_data.reset_index()
    tmi_accu = 0
    atpd_data['tmi_accu'] = 0
    tmi_large_accu = 0
    atpd_data['tmi_large_accu'] = 0
    for x in range(len(atpd_data)):
        tmi_accu += atpd_data.iloc[x]['tmi']
        atpd_data.set_value(x, 'tmi_accu', tmi_accu)
        tmi_large_accu += atpd_data.iloc[x]['tmi_large']
        atpd_data.set_value(x, 'tmi_large_accu', tmi_large_accu)
    return atpd_data


def load_stock_for_plot(stock, days):
    daily_data = pd.read_csv('../stock_data/data/%s.csv' % stock)
    daily_data = daily_data.sort_values(by='date', ascending=True)
    return daily_data.tail(days)


def load_atpdr_for_plot(stock, days):
    atpdr_data = pd.read_csv('../stock_data/qa/atpdr/%s.csv' % stock)
    atpdr_data = atpdr_data.sort_values(by='date', ascending=True)
    return atpdr_data.tail(days)


def load_ma_for_stock_for_plot(stock, ma_params, days):
    try:
        with open("%s/qa/ma/%s/%s.pickle" % (stock_data_root, ma_params, stock), 'rb') as f:
            df = pd.DataFrame.from_dict(pickle.load(f), orient='columns', dtype=None)
    except FileNotFoundError:
        df = None
    df = df.sort_values(by='date', ascending=True)
    return df.tail(days)


def load_adl_for_stock_for_plot(stock, days):
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


def load_vhf_for_stock_for_plot(stock, days):
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


def k_plot(stock, days):
    fonts = [14, 16]
    s_full_name = BASIC_INFO.get_market_code_of_stock(stock)
    # load data from file
    # df = load_stock(stock, days)
    df = get_fitted_data(stock, days, 15, 2)
    df_atpdr = load_atpdr_for_plot(stock, days)
    df_ma3 = load_ma_for_stock_for_plot(stock, 'atpd_3', days)
    df_ma10 = load_ma_for_stock_for_plot(stock, 'atpd_10', days)
    df_ma20 = load_ma_for_stock_for_plot(stock, 'atpd_20', days)
    df_ma40 = load_ma_for_stock_for_plot(stock, 'atpd_40', days)
    df_tmi_accu = calc_tmi_series_for_stock(stock, days)

    last_open = df.tail(1).iloc[-1]['open']
    last_close = df.tail(1).iloc[-1]['close']
    last_high = df.tail(1).iloc[-1]['high']
    last_low = df.tail(1).iloc[-1]['low']
    last_day_msg = ' 开:%.02f 收:%.02f 高:%.02f 低:%.02f' % (last_open, last_close, last_high, last_low)

    # plt.ion()
    fig = plt.figure(figsize=(16, 9), dpi=100)
    N = len(df.date)
    ind = np.arange(N)
    date_list = df['date'].tolist()

    def format_date(x, pos=None):
        # noinspection PyTypeChecker
        thisind = np.clip(int(x + 0.5), 0, N - 1)
        return date_list[thisind]

    matplotlib.rcParams.update({'font.size': fonts[0]})

    # setting axis

    ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=3)
    ax2 = plt.subplot2grid((6, 1), (3, 0), sharex=ax1)
    ax3 = plt.subplot2grid((6, 1), (4, 0), sharex=ax1)
    ax4 = plt.subplot2grid((6, 1), (5, 0), sharex=ax1)

    fig.suptitle(u'%s %s 日线图 %s %s' % (stock, BASIC_INFO.name_dict[stock], df_ma10['date'].tolist()[-1], last_day_msg),
                 fontsize=fonts[1])

    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    legend_list = []
    legend_list2 = []
    legend_list3 = []
    line_width = 1.5

    # setting figures

    p_utl, = ax1.plot(ind, df.upper_trend, 'k-')
    plt.setp(p_utl, linewidth=.5)
    p_btl, = ax1.plot(ind, df.bottom_trend, 'k-')
    plt.setp(p_btl, linewidth=.5)

    p_cost_per_vol_1, = ax1.plot(ind, df_atpdr.cost_per_vol_1, '-',
                                 label=u'1日成交均价： %s' % df_atpdr['cost_per_vol_1'].tolist()[-1])
    plt.setp(p_cost_per_vol_1, linewidth=line_width)
    legend_list.append(p_cost_per_vol_1)

    p_cost_per_vol_3, = ax1.plot(ind, df_atpdr.cost_per_vol_3, '-',
                                 label=u'3日成交均价： %s' % df_atpdr['cost_per_vol_3'].tolist()[-1])
    plt.setp(p_cost_per_vol_3, linewidth=line_width)
    legend_list.append(p_cost_per_vol_3)

    p_vol_per_tick_1, = ax3.plot(ind, df_atpdr.vol_per_tick_1, '-',
                                 label=u'1日每单平均手数: %.2f' % float(df_atpdr['vol_per_tick_1'].tolist()[-1]))
    plt.setp(p_vol_per_tick_1, linewidth=line_width)
    legend_list2.append(p_vol_per_tick_1)
    p_vol_per_tick_3, = ax3.plot(ind, df_atpdr.vol_per_tick_3, '-',
                                 label=u'3日每单平均手数: %.2f' % float(df_atpdr['vol_per_tick_3'].tolist()[-1]))
    plt.setp(p_vol_per_tick_3, linewidth=line_width)
    legend_list2.append(p_vol_per_tick_3)
    leg3 = ax3.legend(handles=legend_list2, loc=2)
    leg3.get_frame().set_alpha(0.1)
    p_df_tmi_accu, = ax4.plot(ind, df_tmi_accu.tmi_accu, '-', label=u'自坐标首日起累积资金流入(万元)')
    plt.setp(p_df_tmi_accu, linewidth=line_width)
    legend_list3.append(p_df_tmi_accu)
    p_df_tmi_large_accu, = ax4.plot(ind, df_tmi_accu.tmi_large_accu, '-', label=u'自坐标首日起累积大单资金流入(万元)')
    plt.setp(p_df_tmi_large_accu, linewidth=line_width)
    legend_list3.append(p_df_tmi_large_accu)
    leg4 = ax4.legend(handles=legend_list3, loc=2)
    leg4.get_frame().set_alpha(0.1)
    # p_ma3, = ax1.plot(ind, df_ma3.ma3, '-', label=u'MA3: %s' % df_ma3['ma3'].tolist()[-1])
    # plt.setp(p_ma3, linewidth=line_width)
    # legend_list.append(p_ma3)
    # p_ma10, = ax1.plot(ind, df_ma10.ma10, '-', label=u'MA10: %s' % df_ma10['ma10'].tolist()[-1])
    # plt.setp(p_ma10, linewidth=line_width)
    # legend_list.append(p_ma10)
    p_ma20, = ax1.plot(ind, df_ma20.ma20, '-', label=u'MA20: %s' % df_ma20['ma20'].tolist()[-1])
    plt.setp(p_ma20, linewidth=line_width)
    legend_list.append(p_ma20)
    p_ma40, = ax1.plot(ind, df_ma40.ma40, '-', label=u'MA40: %s' % df_ma40['ma40'].tolist()[-1])
    plt.setp(p_ma40, linewidth=line_width)
    legend_list.append(p_ma40)
    leg = ax1.legend(handles=legend_list, )
    leg.get_frame().set_alpha(0.5)
    candlestick2_ochl(ax1, df.open, df.close, df.high, df.low, width=0.75, colorup='r', colordown='g', alpha=1)
    vc = volume_overlay(ax2, df.open, df.close, df.volume, colorup='r', colordown='g', width=1, alpha=1.0)
    ax2.add_collection(vc)
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(color='gray', linestyle='-')
    ax1.xaxis.grid(color='gray', linestyle='-')
    ax2.yaxis.grid(color='gray', linestyle='-')
    ax2.xaxis.grid(color='gray', linestyle='-')
    ax3.yaxis.grid(color='gray', linestyle='-')
    ax3.xaxis.grid(color='gray', linestyle='-')

    fig.autofmt_xdate()
    fig.tight_layout()
    plt.subplots_adjust(top=0.92)
    fig.savefig('../stock_data/plots/%s.png' % s_full_name, transparent=False)
    intraday_plot(stock, df['date'].tolist()[-1])
    combine_plots(s_full_name)
    subprocess.call('rm ../stock_data/plots/%s_intraday.png' %
                    s_full_name, shell=True)
    plt.close()


def combine_plots(s_full_name):
    images=[Image.open('../stock_data/plots/%s.png' % s_full_name), Image.open('../stock_data/plots/%s_intraday.png' % s_full_name)]
    widths, heights = zip(*(i.size for i in images))

    max_width = max(widths)
    total_height = sum(heights)

    new_im = Image.new('RGB', (max_width, total_height))
    new_im.paste(images[0], (0, 0))
    new_im.paste(images[1], (0, heights[0]))
    new_im.resize((max_width, total_height), Image.ANTIALIAS)
    new_im.save('../stock_data/plots/%s.png' % s_full_name,optimize=True,quality=95)



def save_fig_pickle(path, fig_param):
    with open(path, 'wb') as f:
        pickle.dump(fig_param, f)


def load_fig_pickle(s_full_name):
    try:
        with open('../stock_data/plots_pickle/%s.pickle' % s_full_name, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError as e:
        logging('load_fig_pickle(): File not found')
        return None


def cvt2gif(stock):
    s_full_name = BASIC_INFO.get_market_code_of_stock(stock)
    img = Image.open('../stock_data/plots/%s.png' % s_full_name)
    img = img.resize((545, 300))
    img.save('../stock_data/plots/%s.png' % s_full_name, 'png')

