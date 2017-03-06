import csv
import json
import os
import pickle
import re
import subprocess
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from stock.common.file_operation import list2csv
from stock.common.file_operation import mkdirs, load_csv, logging
from stock.common.time_util import load_last_date, TimeUtil, return_weekday, update_market_open_date_list, \
    load_market_open_date_list_from
from stock.common.variables import *
from stock.common.daemon_class import DaemonClass

# noinspection PyUnboundLocalVariable
class BasicInfoUpdater:
    def __init__(self):
        self.market_dict = {}
        self.symbol_list = []
        self.market_open_days = []

    @staticmethod
    def _get_sse_company_list():
        print('Updating Shanghai Stock Exchange List')
        req_url = 'http://query.sse.com.cn/security/stock/downloadStockListFile.do'
        get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'Accept-Encoding': 'gzip, deflate, sdch',
                       'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                       'Host': 'query.sse.com.cn',
                       'Referer': 'http://www.sse.com.cn/assortment/stock/list/share/',
                       'Upgrade-Insecure-Requests': '1',
                       'User-Agent': COMMON_VARS_OBJ.AGENT_LIST['User-Agent']}
        get_params = {'csrcCode': None,
                      'stockCode': None,
                      'areaName': None,
                      'stockType': 1}
        s = requests.session()
        result = s.get(req_url, headers=get_headers, params=get_params, verify=False)
        csv_data = result.text
        csv_data = csv_data.replace('\t', ',')
        csv_data = csv_data.replace(' ', '')
        with open('%s/sse_company.csv' % COMMON_VARS_OBJ.stock_data_root, 'wb') as f:
            f.write(csv_data.encode('utf8'))

    @staticmethod
    def _get_szse_sub_company_list(market_type):
        market_type_dict = {'a': ['tab2PAGENUM', 'tab2', 'A股列表'],
                            'zxb': ['tab5PAGENUM', 'tab5', '中小企业板'],
                            'cyb': ['tab6PAGENUM', 'tab6', '创业板']}
        req_url = 'https://www.szse.cn/szseWeb/ShowReport.szse'
        get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'Accept-Encoding': 'gzip, deflate, sdch',
                       'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                       'Upgrade-Insecure-Requests': '1',
                       'User-Agent': COMMON_VARS_OBJ.AGENT['User-Agent']}
        get_params = {'SHOWTYPE': 'xlsx', 'CATALOGID': 1110, market_type_dict[market_type][0]: 1, 'ENCODE': 1,
                      'TABKEY': market_type_dict[market_type][1]}
        s = requests.session()
        result = s.get(req_url, headers=get_headers, params=get_params, verify=False)
        with open('/tmp/szse_company.xlsx', 'wb') as f:
            f.write(result.content)

        data_xls = pd.read_excel('/tmp/szse_company.xlsx', market_type_dict[market_type][2], index_col=None,
                                 converters={'A股代码': str, 'A股上市日期': str})
        data_xls.to_csv('%s/szse_company_%s.csv' % (COMMON_VARS_OBJ.stock_data_root, market_type), encoding='utf-8')

    def _get_szse_company_list(self):
        print('Updating Shenzhen Stock Exchange List')
        self._get_szse_sub_company_list('a')

    @staticmethod
    def _merge_company_list():
        final_list = []
        with open('%s/sse_company.csv' % COMMON_VARS_OBJ.stock_data_root) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                final_list.append(
                    {'market': 'sse', 'code': row['A股代码'], 'name': row['A股简称'], 'timeToMarket': row['A股上市日期'],
                     'totals': float(row['A股总股本']) / 10000, 'outstanding': float(row['A股流通股本']) / 10000})
        with open('%s/szse_company_a.csv' % COMMON_VARS_OBJ.stock_data_root) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                final_list.append(
                    {'market': 'szse', 'code': row['A股代码'], 'name': row['公司简称'], 'timeToMarket': row['A股上市日期'],
                     'totals': float(row['A股总股本'].replace(',', '')) / 100000000,
                     'outstanding': float(row['A股流通股本'].replace(',', '')) / 100000000})
        list2csv(final_list, '%s/basic_info.csv' % COMMON_VARS_OBJ.stock_data_root,
                 col_order=['code', 'name', 'market', 'outstanding', 'totals', 'timeToMarket'])

    def update(self):
        self.market_open_days = load_market_open_date_list_from()
        if not os.path.exists(COMMON_VARS_OBJ.stock_data_root):
            not_exist = True
            os.makedirs(COMMON_VARS_OBJ.stock_data_root)
        else:
            not_exist = False
        if (return_weekday(load_last_date()) == 0) | not_exist:
            self._get_sse_company_list()
            self._get_szse_company_list()
            self._merge_company_list()
        update_market_open_date_list()

        try:
            basic_info_list = load_csv('%s/basic_info.csv' % COMMON_VARS_OBJ.stock_data_root)
        except FileNotFoundError:
            self._get_sse_company_list()
            self._get_szse_company_list()
            self._merge_company_list()
            basic_info_list = load_csv('%s/basic_info.csv' % COMMON_VARS_OBJ.stock_data_root)
        for i in basic_info_list:
            self.market_dict[i['code']] = i['market']
        mkdirs(self.symbol_list)

    @staticmethod
    def _get_announcement_one_day(target_day, fetch_type, market):
        fetch_type = fetch_type
        req_url = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'

        page_num = 1
        final_data_list = []
        post_params = {"Accept": "application/json, text/javascript, */*; q=0.01", "Accept-Encoding": "gzip, deflate",
                       "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6",
                       "Cache-Control": "no-cache",
                       "Connection": "keep-alive",
                       "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                       "User-Agent": COMMON_VARS_OBJ.AGENT_LIST['1'],
                       "X-Requested-With": "XMLHttpRequest"}
        while True:
            print('Getting %d of %s' % (page_num, target_day))
            post_data = {'stock': None, 'searchkey': None, 'plate': None, 'category': None, 'trade': None,
                         'column': market,
                         'columnTitle': '历史公告查询',
                         'pageNum': page_num, 'pageSize': 30, 'tabName': fetch_type, 'sortName': None, 'sortType': None,
                         'limit': None,
                         'showTitle': None, 'seDate': target_day}
            s = requests.session()
            data_got = False
            while not data_got:
                try:
                    result = s.post(req_url, data=post_data, params=post_params, verify=False, timeout=1)
                    data_got = True
                except ConnectionError:
                    pass
                except requests.exceptions.ReadTimeout:
                    pass
                except requests.exceptions.ConnectionError:
                    pass
            result_dict = json.loads(result.text)
            final_data_list += result_dict['announcements']
            if result_dict['hasMore']:
                page_num += 1
            else:
                break
        print('Fetched all announcements %d %s' % (len(final_data_list), target_day))
        return final_data_list

    def get_announcement_all_stock_one_day(self, target_day):
        if os.path.exists('%s/announcements/%s.pickle' % (COMMON_VARS_OBJ.stock_data_root, target_day)):
            return
        print('Fetching announcement of %s' % target_day)
        data = []
        data += self._get_announcement_one_day(target_day, 'fulltext',
                                               'szse')  # market doesn't matter, will fetch all markets
        for i in data:
            i['adjunctUrl'] = 'http://www.cninfo.com.cn/%s' % i['adjunctUrl']
        self._save_announcements(target_day, data)
        return data

    def get_all_announcements(self):
        self.market_open_days = load_market_open_date_list_from()
        file_list = os.listdir('%s/announcements' % COMMON_VARS_OBJ.stock_data_root)
        fetched_days = []
        file_list.remove('fetched_days.pickle')
        for f in file_list:
            day = f.split('.')[0]
            fetched_days.append(day)
        try:
            with open('%s/announcements/fetched_days.pickle' % COMMON_VARS_OBJ.stock_data_root, 'rb') as f:
                fetched_days += pickle.load(f)
        except FileNotFoundError:
            fetched_days += []
        target_days = self.market_open_days
        for day in target_days:
            if day not in fetched_days:
                try:
                    self.get_announcement_all_stock_one_day(day)
                    with open('%s/announcements/fetched_days.pickle' % COMMON_VARS_OBJ.stock_data_root, 'wb') as f:
                        pickle.dump(fetched_days, f, -1)
                    fetched_days.append(day)
                except:
                    raise

    @staticmethod
    def _save_announcements(target_day, data_list):
        subprocess.call("mkdir -p %s/announcements" % COMMON_VARS_OBJ.stock_data_root, shell=True)
        with open('%s/announcements/%s.pickle' % (COMMON_VARS_OBJ.stock_data_root, target_day), 'wb') as f:
            pickle.dump(data_list, f, -1)


class BasicInfoUpdaterDaemon(DaemonClass):
    def __init__(self):
        super().__init__(topic_sub=['basic_info_req','time_util_update'], topic_pub='basic_info_update')
