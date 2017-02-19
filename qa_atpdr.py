#!/usr/bin/python3
# -*- coding: utf-8 -*-

from common_func import *


def calc_atpdr_for_stock(stock):
    atpd_list = load_atpd_data(stock)
    if len(atpd_list) == 0:
        return
    for (idx, line) in enumerate(atpd_list):
        # cost per volume 1 d
        try:
            cost_per_vol = float('%.2f' % (line['cost_sum'] / line['volume_sum']))
        except ZeroDivisionError:
            cost_per_vol = 0
        line['cost_per_vol_1'] = cost_per_vol
        # cost per volume 3 d
        if idx > 1:
            vol3d = atpd_list[idx - 2]['volume_sum'] + atpd_list[idx - 1]['volume_sum'] + atpd_list[idx]['volume_sum']
            cost3d = atpd_list[idx - 2]['cost_sum'] + atpd_list[idx - 1]['cost_sum'] + atpd_list[idx]['cost_sum']
            try:
                cost_per_vol3d = float('%.2f' % (cost3d / vol3d))
            except ZeroDivisionError:
                cost_per_vol3d = 0
        else:
            cost_per_vol3d = None
        line['cost_per_vol_3'] = cost_per_vol3d
        # volume per tick 1 d
        try:
            vol_per_tick = float('%.2f' % (line['volume_sum'] / line['tick_size']))
        except ZeroDivisionError:
            vol_per_tick = 0
        line['vol_per_tick_1'] = vol_per_tick

        # volume per tick 3 d
        if idx > 1:
            vol3d = atpd_list[idx - 2]['volume_sum'] + atpd_list[idx - 1]['volume_sum'] + atpd_list[idx]['volume_sum']
            tick3d = atpd_list[idx - 2]['tick_size'] + atpd_list[idx - 1]['tick_size'] + atpd_list[idx]['tick_size']
            try:
                vol_per_tick3d = float('%.3f' % (vol3d / tick3d))
            except ZeroDivisionError:
                vol_per_tick3d = 0
        else:
            vol_per_tick3d = None
        line['vol_per_tick_3'] = vol_per_tick3d

        # atpdr
        if idx > 0:
            try:
                ratio = float('%.4f' % (line['atpd'] / atpd_list[idx - 1]['atpd']))
            except ZeroDivisionError:
                ratio = 0

        else:
            ratio = 1
        line['atpd_ratio'] = '%.4f' % ratio

    b = pd.DataFrame(atpd_list)
    column_order = ['date', 'cost_per_vol_1', 'cost_per_vol_3', 'vol_per_tick_1', 'vol_per_tick_3', 'atpd_ratio']
    b[column_order].to_csv('../stock_data/qa/atpdr/%s.csv' % stock, index=False)


def calc_atpdr_for_all_stock():
    subprocess.call('mkdir -p ../stock_data/qa/atpdr', shell=True)
    print('Calc atpdr for all stocks')
    for i in BASIC_INFO.symbol_list:
        calc_atpdr_for_stock(i)

