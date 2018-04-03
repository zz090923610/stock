#!/usr/bin/python3
# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

import csv
import os

import pandas as pd
import requests
from tools.data.path_hdl import directory_ensure, file_remove, path_expand
from tools.io import logging

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'


# REGDIR( symbol_list/china )


# noinspection PyUnboundLocalVariable,SpellCheckingInspection
class SymbolListUpdateHdl:
    """
    Get most updated class A stock symbol list from Shanghai Stock Exchange & Shenzhen Stock Exchange
    After update there should be three csv files in registered out_dir
    symbol_list.csv: Combined symbol list from both SSE and SZSE with header
        [symbol,name,market,outstanding,totals,timeToMarket]
    where:
        symbol: Listing symbol of the company
        name:   Listing short name of the company
        market: On which exchange of the company listed, either SSE or SZSE
        outstanding: outstanding shares / 10^8
        totals: Total shares / 10^8
        timeToMarket: Date on which the company was listed.

    sse_company.csv: raw symbol list fetched from SSE website
    szse_company_a: raw Symbol list fetch from SZSE website

    Fetched symbol lists will be saved to $PROGRAM_DATA_ROOT/symbol_list/china/

    # DEPENDENCY( requests pandas xlrd )
    """

    def __init__(self):
        self.market_dict = {}
        self.symbol_list = []
        self.market_open_days = []
        self.out_dir = path_expand('symbol_list/china')
        self.encoding = 'utf-8'

    def _get_sse_company_list(self):
        """
        Get raw listed symbols info from ShanghaiStockExchange official website.
        """
        logging("SymbolListUpdater", '[ INFO ] fetching_from_ShanghaiStockExchange_SSE', method='all')
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
        with open(os.path.join(self.out_dir, "sse_company.csv"), 'wb') as f:
            f.write(csv_data.encode(self.encoding))

    def _get_szse_sub_company_list(self, market_type):
        """
        Get raw listed symbols info from Shenzhen_Stock_Exchange official website.
        :param market_type: there are 3 type of companies listing with type code "a", "zxb", "cyb", with code "a" we
        can fetch all of them.
        """
        import urllib3
        urllib3.disable_warnings()
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
        with open(os.path.join(self.out_dir, "szse_company.xlsx"), 'wb') as f:
            f.write(result.content)

        data_xls = pd.read_excel(os.path.join(self.out_dir, "szse_company.xlsx"), market_type_dict[market_type][2],
                                 index_col=None,
                                 converters={'A股代码': str, 'A股上市日期': str})
        data_xls.to_csv(os.path.join(self.out_dir, "szse_company_%s.csv" % market_type), encoding=self.encoding)
        file_remove(os.path.join(self.out_dir, "szse_company.xlsx"))

    def _get_szse_company_list(self):
        """
        wrapper function of _get_szse_sub_company_list('a')
        """
        logging("SymbolListUpdater", '[ INFO ] fetching_from_Shenzhen_Stock_Exchange_SZSE', method='all')
        self._get_szse_sub_company_list('a')

    def _merge_company_list(self):
        """
        merge listed companies data from both exchange into a csv file, with header:
            [symbol,name,market,outstanding,totals,timeToMarket]
        where:
            symbol: symbol of listed company
            name:   name of listed company
            market: can be sse for ShanghaiStockExchange or szse for Shenzhen_Stock_Exchange
            outstanding:    outstanding shares / 10^8
            totals:         total registered shares / 10^8
            timeToMarket:   date listed on exchange, in format YYYY-MM-DD.
        """
        logging("SymbolListUpdater", '[ INFO ] merging_lists', method='all')
        final_list = []

        with open(os.path.join(self.out_dir, "sse_company.csv"), encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                final_list.append(
                    {'market': 'sse', 'symbol': row['A股代码'], 'name': row['A股简称'], 'timeToMarket': row['A股上市日期'],
                     'totals': float(row['A股总股本']) / 10000, 'outstanding': float(row['A股流通股本']) / 10000})

        with open(os.path.join(self.out_dir, "szse_company_a.csv"), encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                final_list.append(
                    {'market': 'szse', 'symbol': row['A股代码'], 'name': row['公司简称'], 'timeToMarket': row['A股上市日期'],
                     'totals': float(row['A股总股本'].replace(',', '')) / 100000000,
                     'outstanding': float(row['A股流通股本'].replace(',', '')) / 100000000})
        self.list2csv(final_list, os.path.join(self.out_dir, "symbol_list.csv"),
                      col_order=['symbol', 'name', 'market', 'outstanding', 'totals', 'timeToMarket'])

    def list2csv(self, data_list, out_file, col_order=None, add_index=False):
        """
        save a list of dict as a csv file
        :param data_list:
        :param out_file:
        :param col_order:
        :param add_index:
        :return:
        """
        if col_order is None:
            col_order = []
        b = pd.DataFrame(data_list)
        b = b.round({'outstanding': 3, 'totals': 3})
        if len(col_order) == 0:
            b.to_csv(out_file, index=add_index, encoding=self.encoding)
        else:
            b[col_order].to_csv(out_file, index=add_index, encoding=self.encoding)

    def update(self):
        """
        Update all symbol list.
        """
        directory_ensure(self.out_dir)
        logging("SymbolListUpdater", '[ INFO ] start_fetching_symbol_list', method='all')
        self._get_sse_company_list()
        self._get_szse_company_list()
        self._merge_company_list()
        logging("SymbolListUpdater", '[ INFO ] finished_fetching_symbol_list', method='all')


# CMDEXPORT ( FETCH SYMBOL ) update_symbol_list
def update_symbol_list():
    """
     Export this function to Control Framework, a control command like:
                FETCH SYMBOL
    can be added to .ctrl batch file to save some work.
    """
    a = SymbolListUpdateHdl()
    a.update()
