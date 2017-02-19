#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

from common_func import *
from data_announance_parsing import get_parsed_announcement_for_stock
from qa_ma import ma_align


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
    for stock in stock_list:
        s_full_name = BASIC_INFO.get_market_code_of_stock(stock)
        full_name_list.append('%s.png' % s_full_name)
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
            msg += u'<font color="red">连涨 %s 天 [%s] %s</font> %s 上市<br><img src="./%s.png"><br>\n' % (
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
            msg += u'<font color="green">连跌 %s 天 [%s] %s</font> %s 上市<br><img src="./%s.png"><br>\n' % (
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
    email_html = generate_html('http://115.28.142.56/plots/%s.html<br>\nhttp://115.28.142.56/plots/<br>\n' % end_day)
    with open('../stock_data/report/five_days_trend/%s.txt' % end_day, 'wb') as myfile:
        myfile.write(bytes(email_html, encoding='utf-8'))
    download_plots(stock_list_of_plot_to_download)
    with open('../stock_data/plots/%s.html' % end_day, 'wb') as myfile:
        myfile.write(bytes(html, encoding='utf-8'))


if __name__ == '__main__':
    generate_trend_report(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
