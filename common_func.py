import csv
import os
import re
import subprocess
import time
from operator import itemgetter
import requests
import json
import tushare as ts
import pickle
from datetime import date, datetime
import datetime

from bs4 import BeautifulSoup

from variables import *
import pandas as pd
from datetime import timedelta as td
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
    except FileNotFoundError:
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
        self.stock_suspend_day_list = {i: [] for i in self.symbol_list}
        self.stock_trade_day_list = {i: [] for i in self.symbol_list}
        self.load()
        self.symbol_sse = [s for s in self.symbol_list if self.in_sse(s)]
        self.symbol_szse = [s for s in self.symbol_list if self.in_szse(s)]
        self.timestamp = time.time()
        self.s = requests.session()

    def load_suspend_trade_date_list(self):  # FIXME
        for stock in self.symbol_list:
            try:
                with open('../stock_data/dates/stock_suspend_days/%s.pickle' % stock, 'rb') as f:
                    self.stock_suspend_day_list[stock] = pickle.load(f)
            except FileNotFoundError:
                self.stock_suspend_day_list[stock] = []
            self.stock_trade_day_list[stock] = list(
                set(self.market_open_days) - set(self.stock_suspend_day_list[stock]))
            self.stock_trade_day_list[stock].sort()
            self.stock_suspend_day_list[stock].sort()

    def get_link_of_stock(self, stock):
        mkt = ''
        if self.market_dict[stock] == 'sse':
            mkt = 'sh'
        elif self.market_dict[stock] == 'szse':
            mkt = 'sz'
        link = '<a href="http://stocks.sina.cn/sh/?code=%s%s&vt=4">%s</a>\n' % (mkt, stock, stock)
        return link

    @staticmethod
    def get_newest_price_of_stock(stock, price_limit=''):
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
            #self.get_all_announcements()
            self.get_announcement_all_stock_one_day(get_today()) #FIXME
            self.get_all_stock_suspend_list()
        basic_info_list = load_csv('../stock_data/basic_info.csv')
        self.market_open_days = load_market_open_date_list()

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
        self.load_suspend_trade_date_list()

    @staticmethod
    def _handle_an_uls(uls):
        final_list = []
        for line in uls:
            stock = line.find("li", {"class": "ta-1"}).get_text()
            if stock == '代码':
                continue
            name = line.find("li", {"class": "ta-2"}).get_text()
            start_time = line.find("li", {"class": "ta-3"}).get_text()
            end_time = line.find("li", {"class": "ta-4"}).get_text()
            try:
                start_time = re.search(r'([0-9]{4}-[0-9]{2}-[0-9]{2})', start_time).group(0)
            except AttributeError:
                start_time = None
            try:
                end_time = re.search(r'([0-9]{4}-[0-9]{2}-[0-9]{2})', end_time).group(0)
            except AttributeError:
                end_time = None
            final_list.append({'code': stock, 'name': name, 'start_time': start_time, 'end_time': end_time})
        return final_list

    def _get_stock_suspend_list_of_day(self, day):
        print("Fetching %s" % day)
        req_url = 'http://www.cninfo.com.cn/cninfo-new/memo-2'
        get_headers = {
            'Host': 'www.cninfo.com.cn',
            'Referer': 'http://www.cninfo.com.cn/cninfo-new/memo-2',
            'Upgrade-Insecure-Requests': 1,
            'User-Agent': AGENT['1']}
        get_params = {'queryDate': day,
                      'queryType': 'queryType1'}
        result = self.s.get(req_url, headers=get_headers, params=get_params)
        b = result.text
        soup = BeautifulSoup(b, 'lxml')
        c = soup.find("div", {"id": "suspensionAndResumption1"})
        d = c.findAll("div", {"class": "column2"})
        start_idx = 0
        end_idx = 1
        if re.search(u'今起停牌', b) is None:
            start_idx = -999
            end_idx = 0
        if re.search(u'今起复牌', b) is None:
            end_idx = -999
        try:
            start_from_day = self._handle_an_uls(d[start_idx].findAll('ul'))
        except IndexError:
            start_from_day = []
        try:
            end_from_day = self._handle_an_uls(d[end_idx].findAll('ul'))
        except IndexError:
            end_from_day = []
        return start_from_day, end_from_day

    def get_all_stock_suspend_list(self):
        try:
            with open('../stock_data/dates/raw_suspend_date_list.pickle', 'rb') as f:
                final_dict = pickle.load(f)
        except FileNotFoundError:
            final_dict = {}
        for day in self.market_open_days:
            try:
                _ = final_dict[day]
            except KeyError:
                s, e = self._get_stock_suspend_list_of_day(day)
                final_dict[day] = {'start': s, 'end': e}
                with open('../stock_data/dates/raw_suspend_date_list.pickle', 'wb') as f:
                    pickle.dump(final_dict, f, -1)

    def _get_announcement_one_day_one_stock(self, target_day, fetch_type, market):
        fetch_type = fetch_type
        req_url = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'

        page_num = 1
        final_data_list = []
        post_params = {"Accept": "application/json, text/javascript, */*; q=0.01", "Accept-Encoding": "gzip, deflate",
                       "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6",
                       "Cache-Control": "no-cache",
                       "Connection": "keep-alive",
                       "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                       "User-Agent": AGENT['1'],
                       "X-Requested-With": "XMLHttpRequest"}
        while True:
            post_data = {'stock': None, 'searchkey': None, 'plate': None, 'category': None, 'trade': None,
                         'column': market,
                         'columnTitle': '历史公告查询',
                         'pageNum': page_num, 'pageSize': 30, 'tabName': fetch_type, 'sortName': None, 'sortType': None,
                         'limit': None,
                         'showTitle': None, 'seDate': target_day}

            result = self.s.post(req_url, data=post_data, params=post_params)
            result_dict = json.loads(result.text)
            final_data_list += result_dict['announcements']
            if result_dict['hasMore']:
                page_num += 1
            else:
                break
        print('Fetched all announcements %d %s' % (len(final_data_list), target_day))
        return final_data_list

    def get_announcement_all_stock_one_day(self, target_day):
        data = []
        data += self._get_announcement_one_day_one_stock(target_day, 'fulltext',
                                                         'szse')  # market doesn't matter, will fetch all markets
        for i in data:
            i['adjunctUrl'] = 'http://www.cninfo.com.cn/%s' % i['adjunctUrl']
        self._save_announcements(target_day, data)
        return data

    def get_all_announcements(self):
        try:
            with open('../stock_data/announcements/fetched_days.pickle', 'rb') as f:
                fetched_days = pickle.load(f)
        except FileNotFoundError:
            fetched_days = []
        target_days = self.market_open_days
        #for day in target_days:
        #    if day <= '2017-01-01':#FIXME temp workaround
        #        target_days.remove(day)
        for day in target_days:
            if day not in fetched_days:
                try:
                    self.get_announcement_all_stock_one_day(day)
                    with open('../stock_data/announcements/fetched_days.pickle', 'wb') as f:
                        pickle.dump(fetched_days, f, -1)
                    fetched_days.append(day)
                except:
                    raise

    @staticmethod
    def _save_announcements(target_day, data_list):
        subprocess.call("mkdir -p ../stock_data/announcements", shell=True)
        with open('../stock_data/announcements/%s.pickle' % target_day, 'wb') as f:
            pickle.dump(data_list, f, -1)

    @staticmethod
    def load_announcements_for(stock, target_day):
        result = []
        try:
            with open('../stock_data/announcements/%s.pickle' % target_day, 'rb') as f:
                loaded = pickle.load(f)
        except FileNotFoundError:
            loaded = []
        for i in loaded:
            if i['secCode'] == stock:
                result.append(i)
        return result


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
        except FileNotFoundError:
            return []
    return data_list


def load_market_open_date_list_from(given_day):
    try:
        with open('../stock_data/market_open_date_list.pickle', 'rb') as f:
            raw_date = pickle.load(f)
    except FileNotFoundError:
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
    except FileNotFoundError:
        return []


def load_ma_for_stock(stock, ma_params):
    try:
        with open("%s/qa/ma/%s/%s.pickle" % (stock_data_root, ma_params, stock), 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []


def save_market_open_date_list(market_open_date_list):
    with open('../stock_data/market_open_date_list.pickle', 'wb') as f:
        pickle.dump(market_open_date_list, f, -1)


MARKET_OPEN_DATE_LIST = load_market_open_date_list()


def load_trade_pause_date_list_for_stock(stock):
    try:
        with open('../stock_data/trade_pause_date/%s.pickle' % stock, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
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
    except FileNotFoundError:
        return []


def mkdirs(symbol_list):
    for a_dir in DIR_LIST:
        subprocess.call('mkdir -p %s' % a_dir, shell=True)
    for s_code in symbol_list:
        subprocess.call('mkdir -p ../stock_data/tick_data/%s' % s_code, shell=True)


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


def generate_html(msg):
    html = """\
    <html>
      <head></head>
      <meta charset="UTF-8">
      <body>
        <p>
            %s
        </p>
      </body>
    </html>
    """ % msg
    return html
