#!/usr/bin/python3

# !/usr/bin/env python
# -*- coding:utf-8 -*-
import pickle

import six
import pandas as pd
import requests
import json
import time
from threading import Thread

import subprocess

from common_func import get_today

def get_trade_stop_list(day):
    req_url = 'http://query.sse.com.cn/infodisplay/querySpecialTipsInfoByPage.do'
    s = requests.session()
    page_num = 1
    final_data_list = []
    get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, sdch',
                   'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                   'Upgrade-Insecure-Requests': 1,
                   'Referer': 'http://www.sse.com.cn/disclosure/dealinstruc/suspension/',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    get_params = {'jsonCallBack':'jsonpCallback1024000',
                    'isPagination':'true',
                    'searchDate':day,
                    'bgFlag':1,
                    'searchDo':1,
                    'pageHelp.pageSize':25,
                    'pageHelp.pageNo':1,
                    'pageHelp.beginPage':1,
                    'pageHelp.cacheSize':1,
                    'pageHelp.endPage':5,
                    '_': int(time.time() * 10000)}
    result = s.get(req_url, headers=get_headers, params=get_params)
    return result

def get_sse_company_list():
    req_url = 'http://query.sse.com.cn/security/stock/downloadStockListFile.do'
    s = requests.session()
    page_num = 1
    final_data_list = []
    get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, sdch',
                   'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                   'Host': 'query.sse.com.cn',
                   'Referer': 'http://www.sse.com.cn/assortment/stock/list/share/',
                   'Upgrade-Insecure-Requests': 1,
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    get_params = {'csrcCode': None,
                  'stockCode': None,
                  'areaName': None,
                  'stockType': 1}
    result = s.get(req_url, headers=get_headers, params=get_params)
    csv_data = result.text
    csv_data = csv_data.replace('\t', ',')
    csv_data = csv_data.replace(' ', '')
    with open('../stock_data/sse_company.csv', 'wb') as f:
        f.write(csv_data.encode('utf8'))


def _get_szse_company_list(market_type):
    market_type_dict={'a':['tab2PAGENUM', 'tab2','A股列表'],
                      'zxb':['tab5PAGENUM', 'tab5','中小企业板'],
                      'cyb':['tab6PAGENUM', 'tab6','创业板']}
    req_url = 'https://www.szse.cn/szseWeb/ShowReport.szse'
    s = requests.session()
    page_num = 1
    final_data_list = []
    get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, sdch',
                   'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                   'Upgrade-Insecure-Requests': 1,
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    get_params = {'SHOWTYPE': 'xlsx', 'CATALOGID': 1110, market_type_dict[market_type][0]: 1, 'ENCODE': 1, 'TABKEY': market_type_dict[market_type][1]}
    result = s.get(req_url, headers=get_headers, params=get_params)
    with open('/tmp/szse_company.xlsx', 'wb') as f:
        f.write(result.content)
    import pandas as pd
    data_xls = pd.read_excel('/tmp/szse_company.xlsx', market_type_dict[market_type][2], index_col=None)
    data_xls.to_csv('../stock_data/szse_company_%s.csv' % market_type, encoding='utf-8')

def get_szse_company_list():
    _get_szse_company_list('a')
    _get_szse_company_list('zxb')
    _get_szse_company_list('cyb')


def _get_data(date, fetch_type, market):
    date = date
    fetch_type = fetch_type
    market = market
    req_url = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'
    s = requests.session()
    page_num = 1
    final_data_list = []
    post_params = {"Accept": "application/json, text/javascript, */*; q=0.01", "Accept-Encoding": "gzip, deflate",
                   "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6",
                   "Cache-Control": "no-cache",
                   "Connection": "keep-alive",
                   "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
                   "X-Requested-With": "XMLHttpRequest"}
    while True:
        post_data = {'stock': None, 'searchkey': None, 'plate': None, 'category': None, 'trade': None, 'column': market,
                     'columnTitle': '历史公告查询',
                     'pageNum': page_num, 'pageSize': 30, 'tabName': fetch_type, 'sortName': None, 'sortType': None,
                     'limit': None,
                     'showTitle': None, 'seDate': date}

        result = s.post(req_url, data=post_data, params=post_params)
        result_dict = json.loads(result.text)
        final_data_list += result_dict['announcements']
        if result_dict['hasMore']:
            page_num += 1
        else:
            break
    print('Fetched all announcements %d' % len(final_data_list))
    return final_data_list


def save_announcements(date, data_list):
    subprocess.call("mkdir -p ../stock_data/announcements", shell=True)
    with open('../stock_data/announcements/%s.pickle' % date, 'wb') as f:
        pickle.dump(data_list, f, -1)


def load_announcements_for(stock, date):
    result = []
    try:
        with open('../stock_data/announcements/%s.pickle' % date, 'rb') as f:
            loaded = pickle.load(f)
    except:
        loaded = []
    for i in loaded:
        if i['secCode'] == stock:
            result.append(i)
    return result


def fetch_all_announcements(date):
    data = []
    data += _get_data(date, 'fulltext', 'szse')
    data += _get_data(date, 'fulltext', 'sse')
    for i in data:
        i['adjunctUrl'] = 'http://www.cninfo.com.cn/%s' % i['adjunctUrl']
    save_announcements(date, data)
    return data


def get_parsed_announcement_for_stock(stock, date):
    dlist = load_announcements_for(stock, date)
    final_str = ''
    for i in dlist:
        final_str += '<a href="%s">%s</a>\n' % (i['adjunctUrl'], i['announcementTitle'])
    return final_str
