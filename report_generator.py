#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

from common_func import *
from data_announance_parsing import get_parsed_announcement_for_stock
from qa_analysis_collect import *


# noinspection PyShadowingNames
def sorting_attributes(day):
    trend5d_up = []
    trend5d_down = []
    vol_indi = []
    vol_indi_large = []
    for stock in BASIC_INFO.symbol_list:
        a = AnalysisResult(stock)
        try:
            for attr in a.result[day]:
                if attr.find('trend5d') != -1:
                    trend = attr.split('_')[1]
                    days = attr.split('_')[2]
                    if trend == 'up':
                        trend5d_up.append({'code':stock,'continue_days':days})
                    else:
                        trend5d_down.append({'code':stock,'continue_days':days})
                elif attr.find('buy_vol_indi_cont_large') != -1:
                    vi_large = attr.split('_')[5]
                    vi_small = attr.split('_')[6]
                    cont_days = attr.split('_')[7]
                    vol_indi_large.append({'code': stock, 'vol_indi': (vi_large, vi_small, cont_days)})
                elif attr.find('buy_vol_indi') != -1:
                    vi_large = attr.split('_')[3]
                    vi_small = attr.split('_')[4]
                    vol_indi.append({'code': stock, 'vol_indi': (vi_large, vi_small)})

        except KeyError:
            pass
    return trend5d_up, trend5d_down, vol_indi, vol_indi_large


# noinspection PyShadowingNames
def generate_html_vol_indi(vol_indi, day):
    print("Generating VOL_INDI Report")
    msg = u''
    for l in vol_indi:
        s_full_name = BASIC_INFO.get_market_code_of_stock(l['code'])
        large, small = l['vol_indi']
        msg += u'<font color="red">大单增量比: %s 小单增量比: %s [%s] %s</font> %s 上市<br><img src="./%s.png"><br>\n' % (
            large, small, BASIC_INFO.get_link_of_stock(l['code']), BASIC_INFO.name_dict[l['code']],
            BASIC_INFO.time_to_market_dict[l['code']], s_full_name)
        anmt = get_parsed_announcement_for_stock(l['code'], day)
        if len(anmt) > 0:
            msg += '%s<br>\n' % anmt
    html = generate_html(msg)
    with open('../stock_data/plots/%s_vol_indi.html' % day, 'wb') as myfile:
        myfile.write(bytes(html, encoding='utf-8'))


def generate_html_vol_indi_large(vol_indi_large, day):
    print("Generating VOL_INDI_LARGE Report")
    msg = u''
    for l in vol_indi_large:
        s_full_name = BASIC_INFO.get_market_code_of_stock(l['code'])
        large, small, cont_days = l['vol_indi']
        msg += \
            u'<font color="red">连增 %s 天。大单增量比: %s 小单增量比: %s [%s] %s</font> %s 上市<br><img src="./%s.png"><br>\n' % (cont_days,
            large, small, BASIC_INFO.get_link_of_stock(l['code']), BASIC_INFO.name_dict[l['code']],
            BASIC_INFO.time_to_market_dict[l['code']], s_full_name)
        anmt = get_parsed_announcement_for_stock(l['code'], day)
        if len(anmt) > 0:
            msg += '%s<br>\n' % anmt
    html = generate_html(msg)
    with open('../stock_data/plots/%s_vol_indi_large.html' % day, 'wb') as myfile:
        myfile.write(bytes(html, encoding='utf-8'))



def generate_html_trend5d(trend5d_up, trend5d_down, day):
    print("Generating Trend5D Report")
    msg_up = u'%s\n连续五日日平均交易价格上涨股票<br>\n' % day
    msg_down = u'\n连续五日日平均交易价格下跌股票<br>\n'
    u = trend5d_up
    d = trend5d_down
    for l in u:
        l['timeToMarket'] = BASIC_INFO.time_to_market_dict[l['code']]
    for l in d:
        l['timeToMarket'] = BASIC_INFO.time_to_market_dict[l['code']]
    u = sorted(u, key=itemgetter('timeToMarket'))
    d = sorted(d, key=itemgetter('timeToMarket'))
    for l in u:
        s_full_name = BASIC_INFO.get_market_code_of_stock(l['code'])
        msg_up += u'<font color="red">连涨 %s 天 [%s] %s</font> %s 上市<br><img src="./%s.png"><br>\n' % (
            l['continue_days'], BASIC_INFO.get_link_of_stock(l['code']), BASIC_INFO.name_dict[l['code']],
            BASIC_INFO.time_to_market_dict[l['code']], s_full_name)
        anmt = get_parsed_announcement_for_stock(l['code'], day)
        if len(anmt) > 0:
            msg_up += anmt
            msg_up += '<br>\n'
    for l in d:
        s_full_name = BASIC_INFO.get_market_code_of_stock(l['code'])
        msg_down += u'<font color="green">连跌 %s 天 [%s] %s</font> %s 上市<br><img src="./%s.png"><br>\n' % (
            l['continue_days'], BASIC_INFO.get_link_of_stock(l['code']), BASIC_INFO.name_dict[l['code']],
            BASIC_INFO.time_to_market_dict[l['code']], s_full_name)
        anmt = get_parsed_announcement_for_stock(l['code'], day)
        if len(anmt) > 0:
            msg_down += anmt
            msg_down += '<br>\n'
    msg = msg_up + msg_down
    html = generate_html(msg)
    with open('../stock_data/plots/%s.html' % day, 'wb') as myfile:
        myfile.write(bytes(html, encoding='utf-8'))


def generate_email(day):
    email_html = generate_html(
        '<a href="http://115.28.142.56/plots/%s.html">连续五日日平均交易价格变动股票</a><br>\n'
        '<a href="http://115.28.142.56/plots/%s_vol_indi.html">发出大小单增量买入信号股票</a><br>\n'
        '<a href="http://115.28.142.56/plots/%s_vol_indi_large.html">近五日大单增量大于三天股票</a><br>\n'
        '<a href="http://115.28.142.56/plots/">所有股票最新图线</a><br>\n' % (day,day, day))
    with open('../stock_data/report/five_days_trend/%s.txt' % day, 'wb') as myfile:
        myfile.write(bytes(email_html, encoding='utf-8'))


if __name__ == '__main__':
    continue_days = int(sys.argv[1])
    day = sys.argv[2]
    trend5d_up, trend5d_down, vol_indi, vol_indi_large = sorting_attributes(day)
    generate_html_vol_indi(vol_indi, day)
    generate_html_vol_indi_large(vol_indi_large, day)
    generate_html_trend5d(trend5d_up, trend5d_down, day)
    generate_email(day)