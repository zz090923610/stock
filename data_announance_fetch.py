#!/usr/bin/python3

# !/usr/bin/env python
# -*- coding:utf-8 -*-

from common_func import *
import requests
import json
import time
import subprocess


def get_announcements(date, fetch_type, market):
    date = date
    fetch_type = fetch_type
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
    data += get_announcements(date, 'fulltext', 'szse')  # market doesn't matter, will fetch all markets
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
