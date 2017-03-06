#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pickle

import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib import ticker
from mpl_finance import *

from stock.common.common_func import *



def intraday_plot(stock, target_date):
    fonts = [14, 16]
    s_full_name = BASIC_INFO.market_code_of_stock(stock)
    df = load_stock_tick_data(stock, target_date)
    fig = plt.figure(figsize=(16, 6), dpi=100)
    N = len(df.time)
    ind = np.arange(N)
    time_list = df['time'].tolist()

    def format_time(x, pos=None):
        # noinspection PyTypeChecker
        thisind = np.clip(int(x + 0.5), 0, N - 1)
        return time_list[thisind]

    matplotlib.rcParams.update({'font.size': fonts[0]})
    ax1 = plt.subplot2grid((4, 1), (0, 0), rowspan=4)
    fig.suptitle(u'%s %s 日内图 %s' % (stock, BASIC_INFO.name_dict[stock], target_date), fontsize=fonts[1])
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_time))
    legend_list = []
    line_width = 1.5

    p_price, = ax1.plot(ind, df.price, '-', label=u'成交价格')
    plt.setp(p_price, linewidth=line_width)
    legend_list.append(p_price)

    leg = ax1.legend(handles=legend_list, )
    leg.get_frame().set_alpha(0.5)
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(color='gray', linestyle='-')
    ax1.xaxis.grid(color='gray', linestyle='-')
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.subplots_adjust(top=0.92)
    fig.savefig('%s/plots/%s_intraday.png' % (stock_data_root, s_full_name), transparent=False)
    # plt.plot(fig)
    plt.close(fig)


def save_fig_pickle(path, fig_param):
    with open(path, 'wb') as f:
        pickle.dump(fig_param, f)


def load_fig_pickle(s_full_name):
    try:
        with open('%s/plots_pickle/%s.pickle' % (stock_data_root, s_full_name), 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError as e:
        logging('load_fig_pickle(): File not found')
        return None


def cvt2gif(stock):
    s_full_name = BASIC_INFO.market_code_of_stock(stock)
    img = Image.open('%s/plots/%s.png' % (stock_data_root, s_full_name))
    img = img.resize((545, 300))
    img.save('%s/plots/%s.png' % (stock_data_root, s_full_name), 'png')
