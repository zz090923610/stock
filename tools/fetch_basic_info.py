#!/usr/bin/python3

import csv
import os
import sys
import pandas as pd
import requests

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'


def list2csv(data_list, out_file, col_order=None, add_index=False):
    if col_order is None:
        col_order = []
    b = pd.DataFrame(data_list)
    b=b.round({'outstanding': 3, 'totals': 3})
    if len(col_order) == 0:
        b.to_csv(out_file, index=add_index)
    else:
        b[col_order].to_csv(out_file, index=add_index)


# noinspection PyUnboundLocalVariable
class BasicInfoUpdater:
    def __init__(self, out_dir):
        self.market_dict = {}
        self.symbol_list = []
        self.market_open_days = []
        self.out_dir = out_dir

    def _get_sse_company_list(self):
        print('Updating Shanghai Stock Exchange List')
        req_url = 'http://query.sse.com.cn/security/stock/downloadStockListFile.do'
        get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'Accept-Encoding': 'gzip, deflate, sdch',
                       'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                       'Host': 'query.sse.com.cn',
                       'Referer': 'http://www.sse.com.cn/assortment/stock/list/share/',
                       'Upgrade-Insecure-Requests': '1',
                       'User-Agent': USER_AGENT}
        get_params = {'csrcCode': None,
                      'stockCode': None,
                      'areaName': None,
                      'stockType': 1}
        s = requests.session()
        result = s.get(req_url, headers=get_headers, params=get_params, verify=False)
        csv_data = result.text
        csv_data = csv_data.replace('\t', ',')
        csv_data = csv_data.replace(' ', '')
        with open('%s/sse_company.csv' % self.out_dir, 'wb') as f:
            f.write(csv_data.encode('utf8'))

    def _get_szse_sub_company_list(self, market_type):
        market_type_dict = {'a': ['tab2PAGENUM', 'tab2', 'A股列表'],
                            'zxb': ['tab5PAGENUM', 'tab5', '中小企业板'],
                            'cyb': ['tab6PAGENUM', 'tab6', '创业板']}
        req_url = 'https://www.szse.cn/szseWeb/ShowReport.szse'
        get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'Accept-Encoding': 'gzip, deflate, sdch',
                       'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                       'Upgrade-Insecure-Requests': '1',
                       'User-Agent': USER_AGENT}
        get_params = {'SHOWTYPE': 'xlsx', 'CATALOGID': 1110, market_type_dict[market_type][0]: 1, 'ENCODE': 1,
                      'TABKEY': market_type_dict[market_type][1]}
        s = requests.session()
        result = s.get(req_url, headers=get_headers, params=get_params, verify=False)
        with open('%s/szse_company.xlsx'% self.out_dir, 'wb') as f:
            f.write(result.content)

        data_xls = pd.read_excel('%s/szse_company.xlsx'% self.out_dir, market_type_dict[market_type][2], index_col=None,
                                 converters={'A股代码': str, 'A股上市日期': str})
        data_xls.to_csv('%s/szse_company_%s.csv' % (self.out_dir, market_type), encoding='utf-8')
        os.remove('%s/szse_company.xlsx' % self.out_dir)

    def _get_szse_company_list(self):
        print('Updating Shenzhen Stock Exchange List')
        self._get_szse_sub_company_list('a')

    def _merge_company_list(self):
        final_list = []
        with open('%s/sse_company.csv' % self.out_dir) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                final_list.append(
                    {'market': 'sse', 'code': row['A股代码'], 'name': row['A股简称'], 'timeToMarket': row['A股上市日期'],
                     'totals': float(row['A股总股本']) / 10000, 'outstanding': float(row['A股流通股本']) / 10000})
        with open('%s/szse_company_a.csv' % self.out_dir) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                final_list.append(
                    {'market': 'szse', 'code': row['A股代码'], 'name': row['公司简称'], 'timeToMarket': row['A股上市日期'],
                     'totals': float(row['A股总股本'].replace(',', '')) / 100000000,
                     'outstanding': float(row['A股流通股本'].replace(',', '')) / 100000000})
        list2csv(final_list, '%s/basic_info.csv' % self.out_dir,
        col_order=['code', 'name', 'market', 'outstanding', 'totals', 'timeToMarket'])

    def update(self):
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        self._get_sse_company_list()
        self._get_szse_company_list()
        self._merge_company_list()


if __name__ == '__main__':
    if len(sys.argv)>1:
        a = BasicInfoUpdater(sys.argv[1])
        a.update()
