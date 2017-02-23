#!/usr/bin/python3
# -*- coding: utf-8 -*-

import_list = ['import csv',
               'import pickle',
               'import subprocess',
               'import matplotlib',
               'import matplotlib.pyplot as plt',
               'import pandas as pd',
               'from PIL import Image',
               'from matplotlib import ticker',
               'from mpl_finance import *',
               'from common_func import BASIC_INFO, logging',
               'from qa_linear_fit import get_fitted_data',
               'from variables import *',
               'from intraday_plot import intraday_plot']

data_loader_list = [
    {'df_name': 'df', 'load_func': 'get_fitted_data', 'params': 'stock, days, 15, 2'},
    {'df_name': 'df_atpdr', 'load_func': 'load_atpdr_for_plot', 'params': 'stock, days'},
    {'df_name': 'df_ma3', 'load_func': 'load_ma_for_stock_for_plot', 'params': "stock, 'atpd_3', days"},
    {'df_name': 'df_ma10', 'load_func': 'load_ma_for_stock_for_plot', 'params': "stock, 'atpd_10', days"},
    {'df_name': 'df_ma20', 'load_func': 'load_ma_for_stock_for_plot', 'params': "stock, 'atpd_20', days"},
    {'df_name': 'df_ma40', 'load_func': 'load_ma_for_stock_for_plot', 'params': "stock, 'atpd_40', days"},
    {'df_name': 'df_tmi_accu', 'load_func': 'calc_tmi_series_for_stock', 'params': 'stock, days'}
]

figure_setting = {'title': "'%s %s 日线图 %s 开:%.02f 收:%.02f 高:%.02f 低:%.02f' % (stock, BASIC_INFO.name_dict[stock],"
                           "df.iloc[-1]['date'],df.iloc[-1]['open'], df.iloc[-1]['close'],"
                           "df.iloc[-1]['high'], df.iloc[-1]['low'])",
                  'ax_list': []
                  }


# noinspection PyShadowingNames
def add_import(import_list):
    script = ''
    for i in import_list:
        script += '%s\n' % i
    return script


def generate_block(header, body_list):
    # noinspection PyShadowingNames
    script = ''
    current_indent = 0
    script += '%s\n' % header
    current_indent += 1
    for body_item in body_list:
        script += '\t%s\n' % body_item
    return script


func_header = 'def k_plot(stock, days):'
func_body = []


# noinspection PyShadowingNames
def generate_data_load_sentence(data_loader_list):
    script_list = []
    for line in data_loader_list:
        script_list.append('%s=%s(%s)' % (line['df_name'], line['load_func'], line['params']))
    return script_list


script = add_import(import_list)
func_body += (generate_data_load_sentence(data_loader_list))
script += generate_block(func_header, func_body)

with open('./test.py', 'wb') as f:
    f.write(script.encode('utf8'))
