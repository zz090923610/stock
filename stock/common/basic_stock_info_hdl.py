import pickle
import re
import subprocess

from stock.common.file_operation import load_csv
from stock.common.time_util import load_last_date, load_market_open_date_list_from
from stock.common.variables import *


class BasicInfoHDL:
    def __init__(self):
        self.market_dict = {}
        self.name_dict = {}
        self.outstanding_dict = {}
        self.totals_dict = {}
        self.time_to_market_dict = {}
        self.symbol_list = []
        self.market_open_days = []
        self.load()
        self.symbol_sse = [s for s in self.symbol_list if self.in_sse(s)]
        self.symbol_szse = [s for s in self.symbol_list if self.in_szse(s)]

    def load(self):
        basic_info_list = load_csv('%s/basic_info.csv' % COMMON_VARS_OBJ.stock_data_root)
        self.market_open_days = load_market_open_date_list_from()
        for i in basic_info_list:
            try:
                assert i['market'] in ['sse', 'szse']
                assert (re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", i['timeToMarket']) is not None)
                assert (re.match(r"[0-9]{6}", i['code']) is not None)
            except AssertionError as e:
                if i['code'] == '600996':
                    i['timeToMarket'] = '2016-12-26'
                else:
                    e.args += i
                    raise
            self.market_dict[i['code']] = i['market']
            self.name_dict[i['code']] = i['name']
            self.outstanding_dict[i['code']] = i['outstanding']
            self.totals_dict[i['code']] = i['totals']
            self.time_to_market_dict[i['code']] = i['timeToMarket']
            self.symbol_list.append(i['code'])

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

    def market_code_of_stock(self, stock):
        try:
            mkt = ''
            if self.market_dict[stock] == 'sse':
                mkt = 'sh'
            elif self.market_dict[stock] == 'szse':
                mkt = 'sz'
            return '%s%s' % (mkt, stock)
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

    @staticmethod
    def load_announcements_for(stock, target_day):
        result = []
        try:
            with open('%s/announcements/%s.pickle' % (COMMON_VARS_OBJ.stock_data_root, target_day), 'rb') as f:
                loaded = pickle.load(f)
        except FileNotFoundError:
            loaded = []
        for i in loaded:
            if i['secCode'] == stock:
                result.append(i)
        return result
