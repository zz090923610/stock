# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

import os
import re

from tools.data.path_hdl import path_expand
from tools.file_hdl import load_csv


# USEDIR( symbol_list/china )

class SymbolListHDL:
    def __init__(self):
        self.market_dict = {}
        self.name_dict = {}
        self.outstanding_dict = {}
        self.totals_dict = {}
        self.time_to_market_dict = {}
        self.symbol_list = []
        self.load()
        self.symbol_sse = [s for s in self.symbol_list if self.in_sse(s)]
        self.symbol_szse = [s for s in self.symbol_list if self.in_szse(s)]

    def load(self):
        basic_info_list = load_csv(os.path.join(path_expand("symbol_list/china"), 'symbol_list.csv'))
        for i in basic_info_list:
            try:
                assert i['market'] in ['sse', 'szse']
                assert (re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", i['timeToMarket']) is not None)
                assert (re.match(r"[0-9]{6}", i['symbol']) is not None)
            except AssertionError as e:
                if i['symbol'] == '600996':
                    i['timeToMarket'] = '2016-12-26'
                else:
                    e.args += i
                    raise
            self.market_dict[i['symbol']] = i['market']
            self.name_dict[i['symbol']] = i['name']
            self.outstanding_dict[i['symbol']] = i['outstanding']
            self.totals_dict[i['symbol']] = i['totals']
            self.time_to_market_dict[i['symbol']] = i['timeToMarket']
            self.symbol_list.append(i['symbol'])
        self.symbol_list = list(set(self.symbol_list))

    # Below functions should be called after data loaded
    def link_of_stock(self, stock):
        mkt = ''
        try:
            if self.market_dict[stock] == 'sse':
                mkt = 'sh'
            elif self.market_dict[stock] == 'szse':
                mkt = 'sz'
        except KeyError:
            mkt = ''
        link = '<a href="http://stocks.sina.cn/sh/?code=%s%s&vt=4">%s</a>\n' % (mkt, stock, stock)
        return link

    def market_symbol_of_stock(self, stock):
        try:
            mkt = ''
            if self.market_dict[stock] == 'sse':
                mkt = 'sh'
            elif self.market_dict[stock] == 'szse':
                mkt = 'sz'
            return '%s%s' % (mkt, stock)
        except KeyError:
            return ''

    def market_of_stock(self, stock):
        try:
            mkt = ''
            if self.market_dict[stock] == 'sse':
                mkt = 'sh'
            elif self.market_dict[stock] == 'szse':
                mkt = 'sz'
            return mkt
        except KeyError:
            return ''

    def in_sse(self, stock):
        try:
            if self.market_dict[stock] == 'sse':
                return True
            else:
                return False
        except KeyError:
            return False

    def in_szse(self, stock):
        try:
            if self.market_dict[stock] == 'szse':
                return True
            else:
                return False
        except KeyError:
            return False
