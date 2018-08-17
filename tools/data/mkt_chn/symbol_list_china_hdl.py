# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

import os
import re

from tools.data.path_hdl import path_expand
from tools.data.file_hdl import load_csv


# USEDIR( symbol_list/china )

class SymbolListHDL:
    """
    This class handles some vital information of all symbols from both exchanges, actually it maintains several dicts.
    """
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
        """
        Load data from symbol list storage.
        """
        self.symbol_list = []
        basic_info_list = load_csv(os.path.join(path_expand("symbol_list/china"), 'symbol_list.csv'))
        for i in basic_info_list:
            try:
                assert i['market'] in ['sse', 'szse']
                assert (re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", i['timeToMarket']) is not None)
                assert (re.match(r"[0-9]{6}", i['symbol']) is not None)
            except AssertionError as e:
                if i['symbol'] == '600996':  # this is a exception missing data from official source.
                    i['timeToMarket'] = '2016-12-26'
                else:
                    e.args += i
                    raise
                continue
            self.market_dict[i['symbol']] = i['market']
            self.name_dict[i['symbol']] = i['name']
            self.outstanding_dict[i['symbol']] = i['outstanding']
            self.totals_dict[i['symbol']] = i['totals']
            self.time_to_market_dict[i['symbol']] = i['timeToMarket']
            self.symbol_list.append(i['symbol'])

    # Below functions should be called after data loaded
    def link_of_symbol(self, symbol):
        """
        get http link where visual data of symbol can be found.
        :param symbol: symbol, string
        :return: link, string symbol, string
        """
        mkt = ''
        try:
            if self.market_dict[symbol] == 'sse':
                mkt = 'sh'
            elif self.market_dict[symbol] == 'szse':
                mkt = 'sz'
        except KeyError:
            mkt = ''
        link = '<a href="http://stocks.sina.cn/sh/?code=%s%s&vt=4">%s</a>\n' % (mkt, symbol, symbol)
        return link

    def market_code_of_symbol(self, symbol):
        """
        return longer version of symbol prefixed by short exchange code.
        :param symbol: symbol, string
        :return:    string, sh000000 or sz000000
        """
        try:
            mkt = ''
            if self.market_dict[symbol] == 'sse':
                mkt = 'sh'
            elif self.market_dict[symbol] == 'szse':
                mkt = 'sz'
            return '%s%s' % (mkt, symbol)
        except KeyError:
            return ''

    def tushare_pro_symbol(self, symbol):
        """
        :param symbol: symbol, string
        :return:    string, 000000.SH or 000000.SZ
        """
        try:
            mkt = ''
            if self.market_dict[symbol] == 'sse':
                mkt = 'SH'
            elif self.market_dict[symbol] == 'szse':
                mkt = 'SZ'
            return '%s.%s' % (symbol, mkt)
        except KeyError:
            return ''

    def market_of_symbol(self, symbol):
        """
        return exchange code on which the symbol is listed.
        :param symbol:  string
        :return:    sh or sz, prefix version of sse and szse
        """
        try:
            mkt = ''
            if self.market_dict[symbol] == 'sse':
                mkt = 'sh'
            elif self.market_dict[symbol] == 'szse':
                mkt = 'sz'
            return mkt
        except KeyError:
            return ''

    def in_sse(self, symbol):
        """
        check if the symbol is listed on Shanghai Stock Exchange.
        :param symbol:  string
        :return:    boolean
        """
        try:
            if self.market_dict[symbol] == 'sse':
                return True
            else:
                return False
        except KeyError:
            return False

    def in_szse(self, symbol):
        """
        check if the symbol is listed on Shenzhen Stock Exchange.
        :param symbol:  string
        :return:    boolean
        """
        try:
            if self.market_dict[symbol] == 'szse':
                return True
            else:
                return False
        except KeyError:
            return False
