#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from operator import itemgetter

from stock.common.common_func import BASIC_INFO, load_atpdr_data
from stock.quantitative_analysis.qa_analysis_collect import add_analysis_result_one_stock_one_day


def recent_trend_stat(stock, trade_days, last_day):
    atpdr_list_raw = load_atpdr_data(stock)
    atpdr_list = [i for i in atpdr_list_raw if i['date'] <= last_day]
    if len(atpdr_list) < trade_days:
        select_list = atpdr_list
    else:
        select_list = atpdr_list[len(atpdr_list) - trade_days: len(atpdr_list)]
    # noinspection PyShadowingNames
    td = 0
    if len(atpdr_list) < trade_days:
        return 'up', 0, '1970-01-01'
    for i in range(trade_days):
        if (select_list[-1 - i]['atpd_ratio'] - 1) * (select_list[-1]['atpd_ratio'] - 1) > 0:
            td += 1
            continue
        else:
            break
    if select_list[-1]['atpd_ratio'] > 1:
        return 'up', td, select_list[-1]['date']
    else:
        return 'down', td, select_list[-1]['date']


def sort_trend(trade_days, end_day):
    up_list = []
    down_list = []
    for s in BASIC_INFO.symbol_list:
        (trend, continue_day, last_day) = recent_trend_stat(s, trade_days, end_day)
        if (trend == 'up') & (last_day == end_day):
            up_list.append({'code': s, 'trend': trend, 'continue_days': continue_day})
        elif (trend == 'down') & (last_day == end_day):
            down_list.append({'code': s, 'trend': trend, 'continue_days': continue_day})
    return up_list, down_list


def analysis_trend5d(trade_days, continue_days, end_day):
    print("Analysis Trend 5d")
    u, d = sort_trend(trade_days, end_day)
    for l in u:
        l['timeToMarket'] = BASIC_INFO.time_to_market_dict[l['code']]
    for l in d:
        l['timeToMarket'] = BASIC_INFO.time_to_market_dict[l['code']]
    u = sorted(u, key=itemgetter('timeToMarket'))
    d = sorted(d, key=itemgetter('timeToMarket'))
    for l in u:
        if l['continue_days'] >= continue_days:
            add_analysis_result_one_stock_one_day(l['code'], end_day, 'trend5d_up_%s' % l['continue_days'])
    for l in d:
        if l['continue_days'] >= continue_days:
            add_analysis_result_one_stock_one_day(l['code'], end_day, 'trend5d_down_%s' % l['continue_days'])

if __name__ == '__main__':
    analysis_trend5d(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
