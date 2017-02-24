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


def combine_plots(s_full_name):
    images = [Image.open('../stock_data/plots/%s.png' % s_full_name),
              Image.open('../stock_data/plots/%s_intraday.png' % s_full_name)]
    widths, heights = zip(*(i.size for i in images))

    max_width = max(widths)
    total_height = sum(heights)

    new_im = Image.new('RGB', (max_width, total_height))
    new_im.paste(images[0], (0, 0))
    new_im.paste(images[1], (0, heights[0]))
    new_im.resize((max_width, total_height), Image.ANTIALIAS)
    new_im.save('../stock_data/plots/%s.png' % s_full_name, optimize=True, quality=95)


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
