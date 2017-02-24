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


# noinspection PyShadowingNames
def add_import(import_list):
    script = ''
    for i in import_list:
        script += '%s\n' % i
    return script


def generate_block(header, body_str):
    # noinspection PyShadowingNames
    script = ''
    if header != '':
        script += '%s\n' % header
    body_list = body_str.split('\n')
    for body_item in body_list:
        script += '\t%s\n' % body_item
    return script


func_header = 'def k_plot(stock, days):'
func_body = ''


# noinspection PyShadowingNames
def generate_data_load_sentence(data_loader_list):
    script_str = ''
    for line in data_loader_list:
        script_str += '%s=%s(%s)\n' % (line['df_name'], line['load_func'], line['params'])
    return script_str


data_loader_list = [
    {'df_name': 'df', 'load_func': 'get_fitted_data', 'params': 'stock, days, 15, 2'},
    {'df_name': 'df_atpdr', 'load_func': 'load_atpdr_for_plot', 'params': 'stock, days', },
    {'df_name': 'df_ma3', 'load_func': 'load_ma_for_stock_for_plot', 'params': "stock, 'atpd_3', days"},
    {'df_name': 'df_ma10', 'load_func': 'load_ma_for_stock_for_plot', 'params': "stock, 'atpd_10', days"},
    {'df_name': 'df_ma20', 'load_func': 'load_ma_for_stock_for_plot', 'params': "stock, 'atpd_20', days"},
    {'df_name': 'df_ma40', 'load_func': 'load_ma_for_stock_for_plot', 'params': "stock, 'atpd_40', days"},
    {'df_name': 'df_tmi_accu', 'load_func': 'calc_tmi_series_for_stock', 'params': 'stock, days'}
]

plots_list = [
    {'indicator_name': 'main_k', 'data_source': 'df', 'column': ['open', 'high', 'close', 'low'], 'is_date_index': True,
     'shared_x': True, 'span_ratio': 3, 'plot_with': 'self', 'plot_type': 'k_plot', 'legend': 'off',
     'legend_label': None},
    {'indicator_name': 'vol', 'data_source': 'df', 'column': ['volume'], 'is_date_index': False,
     'shared_x': True, 'span_ratio': 1, 'plot_with': 'self', 'plot_type': 'volume', 'legend': 'off',
     'legend_label': None},

    {'indicator_name': 'upper_trend', 'data_source': 'df', 'column': ['upper_trend'], 'is_date_index': False,
     'shared_x': True, 'span_ratio': 3, 'plot_with': 'main_k', 'plot_type': 'line', 'legend': 'off',
     'legend_label': None},

    {'indicator_name': 'bottom_trend', 'data_source': 'df', 'column': ['bottom_trend'], 'is_date_index': False,
     'shared_x': True, 'span_ratio': 3, 'plot_with': 'main_k', 'plot_type': 'line', 'legend': 'off',
     'legend_label': None},

    {'indicator_name': 'cost_per_vol_1', 'data_source': 'df_atpdr', 'column': ['cost_per_vol_1'],
     'is_date_index': False,
     'shared_x': True, 'span_ratio': None, 'plot_with': 'main_k', 'plot_type': 'line', 'legend': 'on',
     'legend_label': "u'1日成交均价： %s' % df_atpdr.iloc[-1]['cost_per_vol_1']"},

    {'indicator_name': 'cost_per_vol_3', 'data_source': 'df_atpdr', 'column': ['cost_per_vol_3'],
     'is_date_index': False,
     'shared_x': True, 'span_ratio': None, 'plot_with': 'main_k', 'plot_type': 'line', 'legend': 'on',
     'legend_label': "u'3日成交均价： %s' % df_atpdr.iloc[-1]['cost_per_vol_3']"},

    {'indicator_name': 'vol_per_tick_1', 'data_source': 'df_atpdr', 'column': ['vol_per_tick_1'],
     'is_date_index': False,
     'shared_x': True, 'span_ratio': 1, 'plot_with': 'self', 'plot_type': 'line', 'legend': 'on',
     'legend_label': "u'1日每单平均手数: %.2f' % float(df_atpdr.iloc[-1]['vol_per_tick_1'])"},

    {'indicator_name': 'vol_per_tick_3', 'data_source': 'df_atpdr', 'column': ['vol_per_tick_3'],
     'is_date_index': False,
     'shared_x': True, 'span_ratio': None, 'plot_with': 'vol_per_tick_1', 'plot_type': 'line', 'legend': 'on',
     'legend_label': "u'3日每单平均手数: %.2f' % float(df_atpdr.iloc[-1]['vol_per_tick_3'])"},

    {'indicator_name': 'ma20', 'data_source': 'df_ma20', 'column': ['ma20'], 'is_date_index': False,
     'shared_x': True, 'span_ratio': None, 'plot_with': 'main_k', 'plot_type': 'line', 'legend': 'on',
     'legend_label': "u'MA20: %s' % df_ma20.iloc[-1]['ma20']"},

    {'indicator_name': 'ma40', 'data_source': 'df_ma40', 'column': ['ma40'], 'is_date_index': False,
     'shared_x': True, 'span_ratio': None, 'plot_with': 'main_k', 'plot_type': 'line', 'legend': 'on',
     'legend_label': "u'MA40: %s' % df_ma40.iloc[-1]['ma40']"},

    {'indicator_name': 'tmi_accu', 'data_source': 'df_tmi_accu', 'column': ['tmi_accu'], 'is_date_index': False,
     'shared_x': True, 'span_ratio': 1, 'plot_with': 'self', 'plot_type': 'line', 'legend': 'on',
     'legend_label': "u'自坐标首日起累积资金流入(万元)'"},

    {'indicator_name': 'tmi_large_accu', 'data_source': 'df_tmi_accu', 'column': ['tmi_large_accu'],
     'is_date_index': False, 'shared_x': True, 'span_ratio': None, 'plot_with': 'tmi_accu', 'plot_type': 'line',
     'legend': 'on',
     'legend_label': "u'自坐标首日起累积大单资金流入(万元)'"}
]

figure_setting = {'title': "'%s %s 日线图 %s 开:%.02f 收:%.02f 高:%.02f 低:%.02f' % (stock, BASIC_INFO.name_dict[stock],"
                           "df.iloc[-1]['date'],df.iloc[-1]['open'], df.iloc[-1]['close'],"
                           "df.iloc[-1]['high'], df.iloc[-1]['low'])",
                  'ax_list': [],
                  'figsize': (16, 9), 'dpi': 100, 'font_size': [14, 16]
                  }


def generate_plot_definition(figure_setting_list, plots_list, data_loader_list):
    final_str = ''
    final_str += 's_full_name = BASIC_INFO.get_market_code_of_stock(stock)\n'
    final_str += 'fig = plt.figure(figsize=%r, dpi=%d)\n' % (figure_setting['figsize'], figure_setting['dpi'])
    final_str += 'fonts = %r\n' % figure_setting['font_size']
    final_str += 'N = len(%s.date)\n' % data_loader_list[0]['df_name']
    final_str += 'ind = np.arange(N)\n'
    final_str += 'date_list = %s[\'date\'].tolist()\n' % data_loader_list[0]['df_name']
    final_str += generate_block('def format_date(x, pos=None):',
                                'thisind = np.clip(int(x + 0.5), 0, N - 1)\nreturn date_list[thisind]\n')
    final_str += 'matplotlib.rcParams.update({\'font.size\': fonts[0]})\n'
    ax_str, leg, ax_dict, leg_dict = generate_ax(plots_list)
    final_str += ax_str
    final_str += 'fig.suptitle(%s)\n' % figure_setting['title']
    for (idx, line) in enumerate(plots_list):
        if line['is_date_index']:
            final_str += 'ax%d.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))\n' % (idx + 1)
    final_str += leg
    for line in plots_list:
        final_str += add_indicator_to_fig(line, ax_dict, leg_dict)

    return final_str


def generate_ax(plots_list):
    final_str = ''
    legend_str = ''
    ax_dict = {}
    legend_dict = {}
    main_plot_cnt = 0
    total_row = 0
    for line in plots_list:
        if line['plot_with'] == 'self':
            total_row += line['span_ratio']

    current_row = 0
    for line in plots_list:
        if line['plot_with'] == 'self':
            main_plot_cnt += 1
            # noinspection SpellCheckingInspection
            ax_dict.update({line['indicator_name']: 'ax%d' % main_plot_cnt})
            final_str += 'ax%d = plt.subplot2grid((%d, 1), (%d, 0), rowspan=%d)\n' % (
                main_plot_cnt, total_row, current_row,
                line['span_ratio'])
            current_row += line['span_ratio']
    leg_cnt = 0
    for line in plots_list:
        if line['legend'] == 'on':
            if line['plot_with'] == 'self':
                if line['indicator_name'] not in legend_dict.keys():
                    legend_str += 'legend_list%d = []\n' % leg_cnt
                    legend_dict.update({line['indicator_name']: 'legend_list%d' % leg_cnt})
                    leg_cnt += 1
            else:
                if line['plot_with'] not in legend_dict.keys():
                    legend_str += 'legend_list%d = []\n' % leg_cnt
                    legend_dict.update({line['plot_with']: 'legend_list%d' % leg_cnt})
                    leg_cnt += 1

    return final_str, legend_str, ax_dict, legend_dict


def add_indicator_to_fig(indi_line, ax_dict, leg_dict):
    final_str = ''
    # "p_utl, = ax1.plot(ind, df.upper_trend, 'k-')"
    if indi_line['plot_type'] == 'line':
        if indi_line['plot_with'] != 'self':
            final_str += "p_%s, = %s.plot(ind, %s.%s, 'k-')\n" % (
                indi_line['indicator_name'], ax_dict[indi_line['plot_with']],
                indi_line['data_source'], indi_line['indicator_name'])
        else:
            final_str += "p_%s, = %s.plot(ind, %s.%s, 'k-')\n" % (
                indi_line['indicator_name'], ax_dict[indi_line['indicator_name']],
                indi_line['data_source'], indi_line['indicator_name'])

        final_str += "plt.setp(p_%s, linewidth=.5)\n" % indi_line['indicator_name']
        # plt.setp(p_utl, linewidth=.5)
        # legend_list.append(p_cost_per_vol_1)
        if indi_line['legend'] == 'on':
            if indi_line['plot_with'] != 'self':
                final_str += "%s.append(p_%s)\n" % (leg_dict[indi_line['plot_with']], indi_line['indicator_name'])
            else:
                final_str += "%s.append(p_%s)\n" % (leg_dict[indi_line['indicator_name']], indi_line['indicator_name'])
    return final_str


script = add_import(import_list)
func_body += (generate_data_load_sentence(data_loader_list))
script += generate_block(func_header, func_body)
script += generate_block('', generate_plot_definition(figure_setting, plots_list, data_loader_list))

with open('./test.py', 'wb') as f:
    f.write(script.encode('utf8'))
