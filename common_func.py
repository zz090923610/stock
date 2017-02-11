import csv
import os
import random
import re
import time
from operator import itemgetter
import requests
import json
import tushare as ts
import pickle
from datetime import date, datetime
import datetime
from threading import Thread
from variables import *
import pandas as pd
from datetime import timedelta as td
import multiprocessing as mp
import operator


def get_operator_fn(op):
    return {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '//': operator.floordiv,
        '%': operator.mod,
        '^': operator.xor,
        '==': operator.eq,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le
    }[op]


def eval_binary_expr(op1, optr, op2):
    return get_operator_fn(optr)(op1, op2)


def list2csv(data_list, out_file, col_order=None, add_index=False):
    if col_order is None:
        col_order = []
    b = pd.DataFrame(data_list)
    if len(col_order) == 0:
        b.to_csv(out_file, index=add_index)
    else:
        b[col_order].to_csv(out_file, index=add_index)


def get_today():
    from datetime import datetime
    current_time = time.time()
    utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(china_tz)
    return local_now.strftime("%Y-%m-%d")


def get_time():
    from datetime import datetime
    current_time = time.time()
    utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(china_tz)
    return local_now.strftime("%Y-%m-%d %H:%M:%S")


def get_time_of_a_day():
    from datetime import datetime
    current_time = time.time()
    utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(china_tz)
    return local_now.strftime("%H:%M:%S")


def load_stock_date_list_from_tick_files(stock):
    file_list = os.listdir('../stock_data/tick_data/%s' % stock)
    if len(file_list) == 0:
        return None
    date_list = []
    for f in file_list:
        day = f.split('_')[1].split('.')[0]
        (y, m, d) = int(day.split('-')[0]), int(day.split('-')[1]), int(day.split('-')[2])
        date_list.append(datetime.datetime(y, m, d).strftime("%Y-%m-%d"))
    return date_list


def check_weekday(date_str):
    (y, m, d) = int(date_str.split('-')[0]), int(date_str.split('-')[1]), int(date_str.split('-')[2])
    if datetime.datetime(y, m, d).weekday() in range(0, 5):
        return True
    else:
        return False


def get_weekends_of_a_year(year):
    d1 = date(int(year), 1, 1)
    d2 = date(int(year), 12, 31)
    days = []
    delta = d2 - d1

    for i in range(delta.days + 1):
        if not check_weekday((d1 + td(days=i)).strftime('%Y-%m-%d')):
            days.append((d1 + td(days=i)).strftime('%Y-%m-%d'))
    return days


def create_market_close_days_for_year(year, other_close_dates_list):
    weekends_list = get_weekends_of_a_year(year)
    for d in other_close_dates_list:
        if d not in weekends_list:
            weekends_list.append(d)
    weekends_list.sort()
    with open('../stock_data/dates/market_close_days_%s.pickle' % year, 'wb') as f:
        pickle.dump(weekends_list, f)


def str2date(str_date):
    (y, m, d) = int(str_date.split('-')[0]), int(str_date.split('-')[1]), int(str_date.split('-')[2])
    return date(y, m, d)


def load_csv(path):
    final_list = []
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            final_list.append(row)
    return final_list


def load_market_open_date_list():
    try:
        with open('../stock_data/market_open_date_list.pickle', 'rb') as f:
            return pickle.load(f)
    except:
        return update_market_open_date_list()


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
        self.stock_suspend_day_list = {i: [] for i in self.symbol_list}
        self.stock_trade_day_list = {i: [] for i in self.symbol_list}
        self.symbol_sse = [s for s in self.symbol_list if self.in_sse(s)]
        self.symbol_szse = [s for s in self.symbol_list if self.in_szse(s)]
        self.timestamp = time.time()
        self.s = requests.session()

    def load_suspend_trade_date_list(self):
        for stock in self.symbol_list:
            try:
                with open('../stock_data/dates/stock_suspend_days/%s.pickle' % stock, 'rb') as f:
                    self.stock_suspend_day_list[stock] = pickle.load(f)
            except:
                self.stock_suspend_day_list[stock] = []
            self.stock_trade_day_list[stock] = list(
                set(self.market_open_days) - set(self.stock_suspend_day_list[stock]))

    def get_link_of_stock(self, stock):
        mkt = ''
        if self.market_dict[stock] == 'sse':
            mkt = 'sh'
        elif self.market_dict[stock] == 'szse':
            mkt = 'sz'
        link = '<a href="http://stocks.sina.cn/sh/?code=%s%s&vt=4">%s</a>\n' % (mkt, stock, stock)
        return link

    def get_newest_price_of_stock(self, stock, price_limit=''):
        data = load_daily_data(stock)
        min_close = min([l['close'] for l in data])
        min_date = ''
        if price_limit != '':
            a = price_limit.split(' ')[0]
            o = price_limit.split(' ')[1]
            b = price_limit.split(' ')[2]
            if a.isdigit():
                a = float(a)
            else:
                a = data[-1][a]
            if b.isdigit():
                b = float(b)
            else:
                b = data[-1][b]
            if not eval_binary_expr(a, o, b):
                return ''
        for i in data:

            if i['close'] == min_close:
                min_date = i['date']
        return '%s %s收盘价 %.02f 2012以来最低收盘价 %s %.02f' % (stock, data[-1]['date'], data[-1]['close'], min_date, min_close)

    def get_market_code_of_stock(self, stock):
        mkt = ''
        if self.market_dict[stock] == 'sse':
            mkt = 'sh'
        elif self.market_dict[stock] == 'szse':
            mkt = 'sz'
        return '%s%s' % (mkt, stock)

    def in_sse(self, stock):
        if self.market_dict[stock] == 'sse':
            return True
        else:
            return False

    def in_szse(self, stock):
        if self.market_dict[stock] == 'szse':
            return True
        else:
            return False

    def _get_sse_company_list(self):
        print('Updating Shanghai Stock Exchange List')
        req_url = 'http://query.sse.com.cn/security/stock/downloadStockListFile.do'
        get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'Accept-Encoding': 'gzip, deflate, sdch',
                       'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                       'Host': 'query.sse.com.cn',
                       'Referer': 'http://www.sse.com.cn/assortment/stock/list/share/',
                       'Upgrade-Insecure-Requests': 1,
                       'User-Agent': AGENT['User-Agent']}
        get_params = {'csrcCode': None,
                      'stockCode': None,
                      'areaName': None,
                      'stockType': 1}
        result = self.s.get(req_url, headers=get_headers, params=get_params)
        csv_data = result.text
        csv_data = csv_data.replace('\t', ',')
        csv_data = csv_data.replace(' ', '')
        with open('../stock_data/sse_company.csv', 'wb') as f:
            f.write(csv_data.encode('utf8'))
        self.timestamp = time.time()

    def _get_szse_sub_company_list(self, market_type):
        market_type_dict = {'a': ['tab2PAGENUM', 'tab2', 'A股列表'],
                            'zxb': ['tab5PAGENUM', 'tab5', '中小企业板'],
                            'cyb': ['tab6PAGENUM', 'tab6', '创业板']}
        req_url = 'https://www.szse.cn/szseWeb/ShowReport.szse'
        get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'Accept-Encoding': 'gzip, deflate, sdch',
                       'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                       'Upgrade-Insecure-Requests': 1,
                       'User-Agent': AGENT['User-Agent']}
        get_params = {'SHOWTYPE': 'xlsx', 'CATALOGID': 1110, market_type_dict[market_type][0]: 1, 'ENCODE': 1,
                      'TABKEY': market_type_dict[market_type][1]}
        result = self.s.get(req_url, headers=get_headers, params=get_params)
        with open('/tmp/szse_company.xlsx', 'wb') as f:
            f.write(result.content)

        data_xls = pd.read_excel('/tmp/szse_company.xlsx', market_type_dict[market_type][2], index_col=None,
                                 converters={'A股代码': str, 'A股上市日期': str})
        data_xls.to_csv('../stock_data/szse_company_%s.csv' % market_type, encoding='utf-8')
        self.timestamp = time.time()

    def _get_szse_company_list(self):
        print('Updating Shenzhen Stock Exchange List')
        self._get_szse_sub_company_list('a')

    def _merge_company_list(self):
        final_list = []
        with open('../stock_data/sse_company.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                final_list.append(
                    {'market': 'sse', 'code': row['A股代码'], 'name': row['A股简称'], 'timeToMarket': row['A股上市日期'],
                     'totals': float(row['A股总股本']) / 10000, 'outstanding': float(row['A股流通股本']) / 10000})
        with open('../stock_data/szse_company_a.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                final_list.append(
                    {'market': 'szse', 'code': row['A股代码'], 'name': row['公司简称'], 'timeToMarket': row['A股上市日期'],
                     'totals': float(row['A股总股本'].replace(',', '')) / 100000000,
                     'outstanding': float(row['A股流通股本'].replace(',', '')) / 100000000})
        list2csv(final_list, '../stock_data/basic_info.csv',
                 col_order=['code', 'name', 'market', 'outstanding', 'totals', 'timeToMarket'])
        self.timestamp = time.time()

    def load(self, update=False):
        if update:
            self._get_sse_company_list()
            self._get_szse_company_list()
            self._merge_company_list()
            update_market_open_date_list()
            self.get_sse_stock_suspend_list_for_all_days('2017-01-16', get_today())
            self.fetch_szse_suspend_list('2017-01-16', get_today())
        basic_info_list = load_csv('../stock_data/basic_info.csv')
        self.market_open_days = load_market_open_date_list()
        self.load_suspend_trade_date_list()
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
            if i['timeToMarket'] > NEW_STOCK_IPO_DATE_THRESHOLD:
                continue
            self.market_dict[i['code']] = i['market']
            self.name_dict[i['code']] = i['name']
            self.outstanding_dict[i['code']] = i['outstanding']
            self.totals_dict[i['code']] = i['totals']
            self.time_to_market_dict[i['code']] = i['timeToMarket']
            self.symbol_list.append(i['code'])

    def get_sse_stock_suspend_list_of_day_one_page(self, day, current_t, current_page, end_page):
        jsoncb = int(current_t + 24 * 3600 * int(day.replace('-', '')))
        try:
            req_url = 'http://query.sse.com.cn/infodisplay/querySpecialTipsInfoByPage.do'
            get_headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                           'Accept-Encoding': 'gzip, deflate, sdch',
                           'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                           'Upgrade-Insecure-Requests': 1,
                           'Referer': 'http://www.sse.com.cn/disclosure/dealinstruc/suspension/',
                           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
            get_params = {'jsonCallBack': 'jsonpCallback%d' % jsoncb,
                          'isPagination': 'true',
                          'searchDate': day,
                          'bgFlag': 1,
                          'searchDo': 1,
                          'pageHelp.pageSize': 25,
                          'pageHelp.pageNo': current_page,
                          'pageHelp.beginPage': current_page,
                          'pageHelp.cacheSize': 1,
                          'pageHelp.endPage': end_page,
                          '_': int(time.time() * 10000)}
            result = self.s.get(req_url, headers=get_headers, params=get_params)
            b = result.text.replace('jsonpCallback%d(' % jsoncb, '')
            b = b.replace(')', '')
            result = json.loads(b)
            final_list = []
            for i in result['result']:
                if (i['stopTime'] == '全天') | (i['stopTime'].find('连续停牌') != -1):
                    final_list.append({'date': day, 'code': i['productCode']})
            self.timestamp = time.time()
            print('Fetched suspend data for day %s, page %d of %d' % (day, current_page, result['pageHelp']['endPage']))
            return final_list, result['pageHelp']['endPage']
        except KeyboardInterrupt:
            raise
        except requests.exceptions.ConnectionError:
            print('Connection Refused')
            return self.get_sse_stock_suspend_list_of_day_one_page(day, jsoncb, current_page, end_page)

    def get_sse_stock_suspend_list_of_day(self, day):
        current_page = 1
        end_page = 5
        final_list = []
        while current_page <= end_page:
            tmp_list, end_page = self.get_sse_stock_suspend_list_of_day_one_page(day, time.time(), current_page,
                                                                                 end_page)
            final_list += tmp_list
            current_page += 1
        return final_list

    def get_sse_stock_suspend_list_for_all_days(self, start_date, end_date):
        all_list = []
        day_list = [day for day in self.market_open_days if (day >= start_date) & (day <= end_date)]
        for day in day_list:
            all_list += self.get_sse_stock_suspend_list_of_day(day)
        for i in all_list:
            if i['code'] in self.symbol_list:
                self.stock_suspend_day_list[i['code']].append(i['date'])
        for stock in self.symbol_list:
            if not BASIC_INFO.in_sse(stock):
                continue
            self.stock_trade_day_list[stock] = list(
                set(self.market_open_days) - set(self.stock_suspend_day_list[stock]))
            with open('../stock_data/dates/stock_trade_days/%s.pickle' % stock, 'wb') as f:
                pickle.dump(self.stock_trade_day_list[stock], f, -1)
            with open('../stock_data/dates/stock_suspend_days/%s.pickle' % stock, 'wb') as f:
                pickle.dump(self.stock_suspend_day_list[stock], f, -1)

    def fetch_szse_suspend_list(self, start_date, end_date):
        total_list = []
        total_list2 = []
        current_page = 1
        end_page = 10
        record_cnt = 0
        id = 0
        s = requests.session()
        while current_page <= end_page:
            req_url = 'http://www.szse.cn/szseWeb/FrontController.szse?randnum=%f' % random.random()
            post_params = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                           'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
                           'Connection': 'keep-alive',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Host': 'www.szse.cn',
                           'Origin': 'http://www.szse.cn',
                           'Referer': 'http://www.szse.cn/main/disclosure/news/tfpts/',
                           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
            if current_page == 1:
                post_data = {'ACTIONID': 7,
                             'AJAX': 'AJAX-TRUE',
                             'CATALOGID': 1798,
                             'TABKEY': 'tab1',
                             'REPORT_ACTION': 'search',
                             'txtKsrq': start_date,
                             'txtZzrq': end_date}
            else:
                post_data = {
                    'ACTIONID': 7,
                    'AJAX': 'AJAX-TRUE',
                    'CATALOGID': 1798,
                    'txtKsrq': start_date,
                    'txtZzrq': end_date,
                    'TABKEY': 'tab1',
                    'tab1PAGENUM': current_page,
                    'tab1PAGECOUNT': end_page,
                    'tab1RECORDCOUNT': record_cnt,
                    'REPORT_ACTION': 'navigate'
                }
            result = s.post(req_url, data=post_data, params=post_params)
            b = result.content.decode('gbk')
            b = b.replace('\r\n', '')
            regex_page_num = r'当前第([0-9]+)页  共([0-9]+)页'
            m = re.search(regex_page_num, b)
            current_page = int(m.group(1))
            end_page = int(m.group(2))
            regex_record_cnt = r'gotoReportPageNoByTextBox\(\'1798\',\'tab1\',\'1798_tab1_naviboxid\',[0-9]+,([0-9]+)\)'
            m = re.search(regex_record_cnt, b)
            record_cnt = int(m.group(1))
            line_regex = r'<tr bgcolor=\'#[0-9a-zA-Z]{6}\' ><td  align=\'center\'  >([0-9]{6})</td><td  width=\'[0-9]*\'  align=\'center\'  >([\u4e00-\u9fa5\uff21-\uff3a\uff41-\uff5aA-Za-z0-9\*\- ]+)</td><td  width=\'[0-9]*\'  align=\'center\'  >([0-9]{4}\-[0-9]{2}\-[0-9]{2})*[\u4e00-\u9fa5\uff21-\uff3a\uff41-\uff5aA-Za-z0-9\*\:, ]*</td><td  width=\'[0-9]*\'  align=\'center\'  >([0-9]{4}\-[0-9]{2}\-[0-9]{2})*[\u4e00-\u9fa5\uff21-\uff3a\uff41-\uff5aA-Za-z0-9\*\:, ]*</td><td  align=\'center\'  >([\u4e00-\u9fa5\uff21-\uff3a\uff41-\uff5aA-Za-z0-9\*\:, ]*)</td><td  align=\'left\'  >([\u4e00-\u9fa5\uff21-\uff3a\uff41-\uff5aA-Za-z0-9\*\:, （）/]*)</td></tr>'
            page_list = []
            while True:
                m = re.search(line_regex, b)
                try:
                    grp_msg = m.groups()
                    page_list.append(
                        {'id': id, 'code': m.group(1), 'start_date': m.group(3), 'end_date': m.group(4),
                         'action': m.group(5),
                         'reason': m.group(6)})
                    total_list.append(
                        {'id': id, 'code': m.group(1), 'start_date': m.group(3), 'end_date': m.group(4),
                         'action': m.group(5),
                         'reason': m.group(6)})
                    id += 1
                    b = b.replace(m.group(0), '')
                except AttributeError:
                    break

            print('%d of %d pages' % (current_page, end_page))
            current_page += 1
            total_list2.append(page_list)
        try:
            assert (len(total_list) == record_cnt)
        except AssertionError:
            print(record_cnt, len(total_list))
            raise
        total_list = sorted(total_list, key=itemgetter('id'))
        stock_suspend_dict = {s: [] for s in BASIC_INFO.symbol_szse}
        for item in total_list:
            if item['code'] in BASIC_INFO.symbol_szse:
                stock_suspend_dict[item['code']].append(item)
        for stock in BASIC_INFO.symbol_szse:
            if len(stock_suspend_dict[stock]) != 0:
                self.generate_szse_suspend_list_of_a_stock(stock, stock_suspend_dict[stock])
            self.stock_suspend_day_list[stock] = list(set(self.stock_suspend_day_list[stock]))
            self.stock_trade_day_list[stock] = list(
                set(self.market_open_days) - set(self.stock_suspend_day_list[stock]))
            with open('../stock_data/dates/stock_trade_days/%s.pickle' % stock, 'wb') as f:
                pickle.dump(self.stock_trade_day_list[stock], f, -1)
            with open('../stock_data/dates/stock_suspend_days/%s.pickle' % stock, 'wb') as f:
                pickle.dump(self.stock_suspend_day_list[stock], f, -1)

    def generate_szse_suspend_list_of_a_stock(self, stock, input_list):
        while len(input_list):
            l = input_list[0]
            start_date = l['start_date']
            end_date = l['end_date']
            if (start_date is not None) & (end_date is not None):
                if start_date == end_date:
                    input_list.remove(l)
                    continue
                else:
                    self.add_stock_suspend_date_between_two_date(stock, start_date, end_date)
                    input_list.remove(l)
                    continue
            if end_date is not None:
                try:
                    start_date = input_list[1]['start_date']
                    next_l = input_list[1]
                    assert (start_date is not None)
                    self.add_stock_suspend_date_between_two_date(stock, start_date, end_date)
                    input_list.remove(l)
                    input_list.remove(next_l)
                    continue
                except AssertionError as e:
                    input_list.remove(l)
                    # print(e, input_list)
                    continue
                except IndexError:
                    self.add_stock_suspend_date_between_two_date(stock, START_DATE, end_date)
                    input_list.remove(l)
                    continue
            if start_date is not None:
                self.add_stock_suspend_date_between_two_date(stock, start_date, get_today())
                input_list.remove(l)

    def add_stock_suspend_date_between_two_date(self, stock, day1, day2):
        date_list = BASIC_INFO.market_open_days
        suspend_list = []
        for day in date_list:
            if (day >= day1) & (day < day2):
                suspend_list.append(day)
        self.stock_suspend_day_list[stock] += suspend_list


BASIC_INFO = BasicInfoHDL()


def update_basic_info():
    BASIC_INFO.load(update=True)


def load_symbol_list(symbol_file):
    symbol_list = []
    if not os.path.isfile(symbol_file):
        update_basic_info()
    with open(symbol_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['timeToMarket'] != '0':
                symbol_list.append(row['code'])
    return symbol_list


def update_market_open_date_list():
    b = ts.get_k_data('000001', index=True, start=START_DATE)
    days_cnt = len(b.index)
    days_list = []
    for idx in range(0, days_cnt):
        days_list.append(b.iloc[idx].date)
    save_market_open_date_list(days_list)
    return days_list


def get_au_scaler_list_of_stock(stock):
    qfq = load_daily_data(stock)
    nonfq = load_daily_data(stock, autype='non_fq')
    result = {}
    for (price_qfq, price_non_fq) in zip(qfq, nonfq):
        result[price_qfq['date']] = price_qfq['close'] / price_non_fq['close']
    return result


def get_au_scaler_of_stock(stock, day):
    qfq = load_daily_data(stock)
    nonfq = load_daily_data(stock, autype='non_fq')
    price_qfq = 1
    price_non_fq = 1

    for line in qfq:
        if line['date'] == day:
            price_qfq = line['close']
            break
    for line in nonfq:
        if line['date'] == day:
            price_non_fq = line['close']
            break
    return price_qfq / price_non_fq


def load_tick_data(stock, day, scaler=1):
    data_list = []
    with open('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, day)) as csvfile:
        reader = csv.DictReader(csvfile)
        try:
            for row in reader:
                row['price'] = float('%.2f' % (float(row['price']) * scaler))
                row['volume'] = int(row['volume'])
                row['amount'] = float(row['amount'])
                data_list.append(row)
        except:
            return []
    return data_list


def load_market_open_date_list_from(given_day):
    try:
        with open('../stock_data/market_open_date_list.pickle', 'rb') as f:
            raw_date = pickle.load(f)
    except:
        raw_date = update_market_open_date_list()
    result_list = []
    for day in raw_date:
        if day >= given_day:
            result_list.append(day)
    return result_list


def load_market_close_days_for_year(year):
    try:
        with open('../stock_data/dates/market_close_days_%s.pickle' % year, 'rb') as f:
            return pickle.load(f)
    except:
        return []


def load_ma_for_stock(stock, ma_params):
    try:
        with open("%s/qa/ma/%s/%s.pickle" % (stock_data_root, ma_params, stock), 'rb') as f:
            return pickle.load(f)
    except:
        return []


def save_market_open_date_list(market_open_date_list):
    with open('../stock_data/market_open_date_list.pickle', 'wb') as f:
        pickle.dump(market_open_date_list, f, -1)


MARKET_OPEN_DATE_LIST = load_market_open_date_list()


def load_trade_pause_date_list_for_stock(stock):
    try:
        with open('../stock_data/trade_pause_date/%s.pickle' % stock, 'rb') as f:
            return pickle.load(f)
    except:
        return []


def load_basic_info_list():
    basic_info_list = []
    with open('../stock_data/basic_info.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            basic_info_list.append(row)
    basic_info_dict = {}
    for line in basic_info_list:
        basic_info_dict[line['code']] = line
    return basic_info_dict


BASIC_INFO_DICT = load_basic_info_list()


def print_basic_info(stock):
    basic_info = BASIC_INFO_DICT[stock]
    print('代码: {} 名称: {} 所属行业: {} 地区: {} \n\
市盈率: {} 流通股本(亿): {} 总股本(亿): {} 总资产(万): {} \n\
流动资产: {} 固定资产: {} 公积金: {} 每股公积金: {} 每股收益: {} \n\
每股净资: {} 市净率: {} 上市日期: {} 未分利润: {} 每股未分配: {}\n\
收入同比(%): {} 利润同比(%): {} 毛利率(%): {} 净利润率(%): {} 股东人数: {}'
          .format(basic_info['code'],
                  basic_info['name'],
                  basic_info['industry'],
                  basic_info['area'],
                  basic_info['pe'],
                  basic_info['outstanding'],
                  basic_info['totals'],
                  basic_info['totalAssets'],
                  basic_info['liquidAssets'],
                  basic_info['fixedAssets'],
                  basic_info['reserved'],
                  basic_info['reservedPerShare'],
                  basic_info['esp'],
                  basic_info['bvps'],
                  basic_info['pb'],
                  basic_info['timeToMarket'],
                  basic_info['undp'],
                  basic_info['perundp'],
                  basic_info['rev'],
                  basic_info['profit'],
                  basic_info['gpr'],
                  basic_info['npr'],
                  basic_info['holders']))


def save_trade_pause_date_date_list_for_stock(stock, pause_list):
    with open('../stock_data/trade_pause_date/%s.pickle' % stock, 'wb') as f:
        pickle.dump(pause_list, f, -1)


def get_stock_open_date_list(stock_ipo_date):
    stock_date_list = []
    for day in MARKET_OPEN_DATE_LIST:
        if day >= stock_ipo_date:
            stock_date_list.append(day)
    return stock_date_list


def get_date_list(start, end, delta):
    curr = str2date(start)
    end = str2date(end)
    date_list = []
    while curr < end:
        date_list.append(curr.strftime("%Y-%m-%d"))
        curr += delta
    return date_list


def load_stock_date_list_from_daily_data(stock):
    date_list = []
    with open('../stock_data/data/%s.csv' % stock) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date_list.append(row['date'])
    return date_list


def load_atpd_data(stock):
    """
    Average Trade Price daily.
    :param stock:
    :return:
    """
    data_list = []
    try:
        with open('../stock_data/qa/atpd/%s.csv' % stock) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['atpd'] = float(row['atpd'])
                data_list.append(row)
        data_new_sorted = sorted(data_list, key=itemgetter('date'))
        return data_new_sorted
    except:
        return []


def mkdirs(symbol_list):
    try:
        if not os.path.isdir('../stock_data/tick_data'):
            os.mkdir('../stock_data/tick_data', mode=0o777)
        for s_code in symbol_list:
            if not os.path.isdir('../stock_data/tick_data/%s' % s_code):
                os.mkdir('../stock_data/tick_data/%s' % s_code, mode=0o777)
    except KeyboardInterrupt:
        exit(0)
    except:
        pass


def load_daily_data(stock, autype='qfq'):
    data_list = []
    if autype == 'qfq':
        with open('../stock_data/data/%s.csv' % stock) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['open'] = float(row['open'])
                row['high'] = float(row['high'])
                row['close'] = float(row['close'])
                row['low'] = float(row['low'])
                row['volume'] = round(float(row['volume']))
                data_list.append(row)
    elif autype == 'non_fq':
        with open('../stock_data/data/%s_non_fq.csv' % stock) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['open'] = float(row['open'])
                row['high'] = float(row['high'])
                row['close'] = float(row['close'])
                row['low'] = float(row['low'])
                row['volume'] = round(float(row['volume']))
                data_list.append(row)
    data_new_sorted = sorted(data_list, key=itemgetter('date'))
    return data_new_sorted
