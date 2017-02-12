#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess
from math import log
from multiprocessing.pool import Pool
from operator import itemgetter
import pandas as pd
import sys

from common_func import *
import numpy as np
import multiprocessing as mp

from data_announance_parsing import get_parsed_announcement_for_stock
from qa_ma import ma_align


def calc_average_trade_price_for_stock_one_day(stock, day, scaler=1):
    print('calc ATPD for %s %s %.03f' % (stock, day, scaler))
    tick_day = load_tick_data(stock, day, scaler=scaler)
    vol_sum = 0
    cost_sum = 0
    for line in tick_day:
        cost_sum += line['price'] * line['volume']
        vol_sum += line['volume']
    try:
        result = '%.2f' % (cost_sum / vol_sum)
    except ZeroDivisionError:
        result = -1
    return {'date': day, 'atpd': result}


def calc_average_trade_price_for_stock(stock, refresh=False):
    print('calc atpd for %s' % stock)
    scaler_list = get_au_scaler_list_of_stock(stock)
    date_list = [i for i in scaler_list.keys()]
    if refresh:
        atpd_list = []
    else:
        atpd_list = load_atpd_data(stock)
    atpd_calced_date_list = [d['date'] for d in atpd_list]
    to_do_date_list = []
    for d in date_list:
        if d not in atpd_calced_date_list:
            to_do_date_list.append(d)
    for i in to_do_date_list:
        atpd_list.append(calc_average_trade_price_for_stock_one_day(stock, i, scaler_list[i]))
    atpd_list_sorted = sorted(atpd_list, key=itemgetter('date'))
    b = pd.DataFrame(atpd_list_sorted)
    column_order = ['date', 'atpd']
    b[column_order].to_csv('../stock_data/qa/atpd/%s.csv' % stock, index=False)


def calc_atpd_for_all_stock(refresh=False):
    pool = mp.Pool()
    for i in BASIC_INFO.symbol_list:
        pool.apply_async(calc_average_trade_price_for_stock, args=(i, refresh))
    pool.close()
    pool.join()


def calc_atpdr_for_stock(stock):
    print('Calc atpdr for %s' % stock)
    atpd_list = load_atpd_data(stock)
    for (idx, line) in enumerate(atpd_list):
        if idx > 0:
            ratio = line['atpd'] / atpd_list[idx - 1]['atpd']
        else:
            ratio = 1
        line['atpd_ratio'] = '%.4f' % ratio
    b = pd.DataFrame(atpd_list)
    column_order = ['date', 'atpd_ratio']
    b[column_order].to_csv('../stock_data/qa/atpdr/%s.csv' % stock, index=False)


def calc_atpdr_for_all_stock():
    for i in BASIC_INFO.symbol_list:
        calc_atpdr_for_stock(i)


def load_atpdr_data(stock):
    """
    Average Trade Price daily.
    :param stock:
    :return:
    """
    data_list = []
    try:
        with open('../stock_data/qa/atpdr/%s.csv' % stock) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['atpd_ratio'] = float(row['atpd_ratio'])
                data_list.append(row)
        data_new_sorted = sorted(data_list, key=itemgetter('date'))
        return data_new_sorted
    except:
        return []


def recent_trend_stat(stock, trade_days, last_day):
    atpdr_list_raw = load_atpdr_data(stock)
    atpdr_list = [i for i in atpdr_list_raw if i['date'] <= last_day]
    if len(atpdr_list) < trade_days:
        select_list = atpdr_list
    else:
        select_list = atpdr_list[len(atpdr_list) - trade_days: len(atpdr_list)]
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


def print_trend(trade_days, continue_days, end_day):
    u, d = sort_trend(trade_days, end_day)
    for l in u:
        if l['continue_days'] >= continue_days:
            print(l)
    for l in d:
        if l['continue_days'] >= continue_days:
            print(l)


def load_basic_info_list():
    symbol_dict = {}
    if not os.path.isfile('../stock_data/basic_info.csv'):
        update_basic_info()
    with open('../stock_data/basic_info.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            (y, m, d) = row['timeToMarket'][0:4], row['timeToMarket'][4:6], row['timeToMarket'][6:8]
            symbol_dict[row['code']] = {'timeToMarket': '%s-%s-%s' % (y, m, d), 'name': row['name']}
    return symbol_dict


def download_plots(stock_list):
    full_name_list = []
    subprocess.call("mkdir -p ../stock_data/plots; rm ../stock_data/plots/*", shell=True)
    for stock in stock_list:
        s_full_name = BASIC_INFO.get_market_code_of_stock(stock)
        subprocess.call("wget http://image.sinajs.cn/newchart/daily/n/%s.gif -O ../stock_data/plots/%s.gif" %
                        (s_full_name, s_full_name), shell=True)  # FIXME try not use subprocess
        full_name_list.append('%s.gif' % s_full_name)
    with open('../stock_data/plots/plot_list.pickle', 'wb') as f:
        pickle.dump(full_name_list, f, protocol=2)


def generate_trend_report(trade_days, continue_days, end_day):
    print("Generating Finance Report")
    stock_list_of_plot_to_download = []
    msg = u'%s\n连续五日日平均交易价格上涨股票<br>\n' % end_day
    u, d = sort_trend(trade_days, end_day)
    for l in u:
        l['timeToMarket'] = BASIC_INFO.time_to_market_dict[l['code']]
    for l in d:
        l['timeToMarket'] = BASIC_INFO.time_to_market_dict[l['code']]
    u = sorted(u, key=itemgetter('timeToMarket'))
    d = sorted(d, key=itemgetter('timeToMarket'))
    for l in u:
        if l['continue_days'] >= continue_days:
            s_full_name = BASIC_INFO.get_market_code_of_stock(l['code'])
            msg += u'<font color="red">连涨 %s 天 [%s] %s</font> %s 上市<br><img src="cid:%s.gif"><br>\n' % (
                l['continue_days'], BASIC_INFO.get_link_of_stock(l['code']), BASIC_INFO.name_dict[l['code']],
                BASIC_INFO.time_to_market_dict[l['code']], s_full_name)
            a = ma_align(l['code'], 10, 20, 40)
            r, out = a.analysis_align_for_day(end_day)
            if len(out) > 0:
                msg += u'%s<br>\n' % out
            anmt = get_parsed_announcement_for_stock(l['code'], end_day)
            if len(anmt) > 0:
                msg += anmt
                msg += '<br>\n'
            stock_list_of_plot_to_download.append(l['code'])

    msg += u'\n连续五日日平均交易价格下跌股票<br>\n'
    for l in d:
        if l['continue_days'] >= continue_days:
            s_full_name = BASIC_INFO.get_market_code_of_stock(l['code'])
            msg += u'<font color="green">连跌 %s 天 [%s] %s</font> %s 上市<br><img src="cid:%s.gif"><br>\n' % (
                l['continue_days'], BASIC_INFO.get_link_of_stock(l['code']), BASIC_INFO.name_dict[l['code']],
                BASIC_INFO.time_to_market_dict[l['code']], s_full_name)
            a = ma_align(l['code'], 10, 20, 40)
            r, out = a.analysis_align_for_day(end_day)
            if len(out) > 0:
                msg += u'%s<br>\n' % out
            anmt = get_parsed_announcement_for_stock(l['code'], end_day)
            if len(anmt) > 0:
                msg += anmt
                msg += '<br>\n'
            stock_list_of_plot_to_download.append(l['code'])
    html = generate_html(msg)
    with open('../stock_data/report/five_days_trend/%s.txt' % end_day, 'wb') as myfile:
        myfile.write(bytes(html, encoding='utf-8'))
    download_plots(stock_list_of_plot_to_download)


if __name__ == '__main__':
    calc_atpd_for_all_stock()
    calc_atpdr_for_all_stock()
    generate_trend_report(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
