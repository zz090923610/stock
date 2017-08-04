# Version 0.2.1
# Author Zhao Zhang<zz156@georgetown.edu>
# stock/common/date_time.py
# dependency: tushare:ts.get_k_data
# 日期/时间模块
# 一切日期时间相关函数的集成模块. 提供当前时刻不同市场的状态.
# 对于已开盘市场, 提供已开盘时长, 当日剩余交易时长, 剩余时长/已开盘时长　等信息
# 对于任意市场, 提供最近一次已完成交易日日期.
# 对于任意市场, 提供开市日历.
# 基本市场信息配置文件格式:
# MARKET CHN/US
# BASIC_OPEN_DATE WEEKDAY
# SPECIAL_CLOSE_DATE_FILE path/to/file
# STATUS PRE_MARKET/OPEN/AFTER_HOUR/CLOSE
# BEGIN 06:00:00
# END 09:29:55
# 特殊开休市时间列表的格式转换/获取

###################################
#
# 　１，查询某特定市场当前状态的函数
#       def get_market_status(mkt_code):
#       input: market code
#       return: period, status, time_avail_today, time_elapsed_today,
#               time_elapsed_today/(time_avail_today+time_elapsed_today)
#
# 　２，查询某特定市场最近一个已结束的交易日期
#       def get_latest_closed_date(mkt_code):
#       input: market code
#       return: last_trade_date
#
#   ３，市场交易日历
#       def get_market_calendar(mkt_code):
#       input: market code
#       return: list of (date, status) pair
#
#
#
#
#


import os
import re

import pytz
import tushare as ts
import datetime
from datetime import date
from datetime import timedelta as td
import pandas as pd
from stock_v2.common.essential import internet_on
import time

I18N = 'CHN'  # FIXME: need to implement full i18n support


def get_market_open_date_list_history_CHN(start='', end=''):
    """
    This function returns a market open date list of China in YYYY-MM-DD format,
    data source is Shanghai Composite Index, from tushare.
    :third-party-dependency: tushare
    :import: import tushare as ts
    :param start: Start date, included in returned list
    :param end: End date, included in returned list
    :return: ['2011-01-01','2012-02-02']
    """
    if internet_on():
        try:
            b = ts.get_k_data('000001', index=True, start=start, end=end)
            days_list = b['date'].tolist()
        except Exception as e:
            days_list = []
            pass  # TODO MQTT ERROR LOG
    else:
        days_list = []
        pass  # TODO MQTT ERROR LOG
    return days_list


def get_market_open_date_list_history_US(start='', end=''):
    # TODO
    return []


def generate_date_range(start='', end='', only='weekday', tz='Asia/Shanghai'):
    """
    This function generate a list of dates based on given range.
    :param tz: time zone
    :third-party-dependency:
    :import:    from datetime import date
                from datetime import timedelta as td
    :param only:
    :param start: Start date, included in returned list, default today - 180
    :param end: End date, included in returned list, default today
    :param only: date type: only weekday, weekend, or all
    :return: ['2011-01-01','2012-02-02']
    """
    start = date_offset(offset=-180) if start == '' else start
    end = get_today(tz=tz) if end == '' else end
    start_in_list = [int(i) for i in start.split('-')]
    end_in_list = [int(i) for i in end.split('-')]
    assert len(start_in_list) == 3
    assert len(end_in_list) == 3
    d1 = date(start_in_list[0], start_in_list[1], start_in_list[2])
    d2 = date(end_in_list[0], end_in_list[1], end_in_list[2])
    delta = d2 - d1
    if only == 'weekday':
        days = []
        for i in range(delta.days + 1):
            if check_weekday((d1 + td(days=i)).strftime('%Y-%m-%d')):
                days.append((d1 + td(days=i)).strftime('%Y-%m-%d'))
    elif only == 'weekend':
        days = []
        for i in range(delta.days + 1):
            if not check_weekday((d1 + td(days=i)).strftime('%Y-%m-%d')):
                days.append((d1 + td(days=i)).strftime('%Y-%m-%d'))
    else:
        days = [(d1 + td(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]
    return days


def get_today(tz='Asia/Shanghai'):
    """
    return today's date in YYYY-MM-DD format
    :param tz: time zone
    :return: string
    """
    from datetime import datetime
    current_time = time.time()
    utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(tz))
    local_today = local_now.strftime("%Y-%m-%d")
    return local_today


def str2date(str_date):
    """
    generate a date obj given an date in string format, YYYY-MM-DD
    :param str_date: given an date in string format, YYYY-MM-DD
    :return: date object
    """
    str_date_in_list = [int(i) for i in str_date.split('-')]
    return date(str_date_in_list[0], str_date_in_list[1], str_date_in_list[2])


def date_offset(start_date='', offset=-7, tz='Asia/Shanghai'):
    start_date = get_today(tz=tz) if start_date == '' else start_date
    target_date = str2date(start_date) + datetime.timedelta(offset)
    return str(target_date)


def check_weekday(target_date):
    target_date = str2date(target_date) if type(target_date) == str else target_date
    if target_date.weekday() in range(0, 5):
        return True
    else:
        return False


class MktCalendar:
    def __init__(self, mkt):
        self.calendar_df = None
        self.dates_previous = None
        self.dates_future = None
        self.calendar_dict = {}
        self.mkt = mkt
        self.mkt_info = MktInfo(self.mkt)
        self.calendar_path = './configs/date_time/calendar/%s.csv' % self.mkt
        self.mkt_info_path = './configs/date_time/%s.cfg' % self.mkt

    def local_today(self):
        return get_today(tz=self.mkt_info.timezone)

    def load_calendar(self):
        self.mkt_info.load_config(self.mkt_info_path)
        if os.path.exists(self.calendar_path):
            self.calendar_df = pd.read_csv(self.calendar_path)
            today = get_today(tz=self.mkt_info.timezone)
            self.dates_previous = self.calendar_df[self.calendar_df['date'] < today]['date'].tolist()
            self.dates_future = self.calendar_df[self.calendar_df['date'] > today]['date'].tolist()
            for index, row in self.calendar_df.iterrows():
                self.calendar_dict[row['date']] = {'mkt_open': row['mkt_open'], 'weekday': row['weekday']}
        else:
            pass
            print('Calendar not found, ', self.calendar_path)
            # TODO: MQTT ERROR LOG

    def check_date(self, target_date):
        try:
            return self.calendar_dict[target_date]
        except KeyError:
            return {'mkt_open': None, 'weekday': None}

    def update(self):
        pass


class Period:
    def __init__(self, name, status, begin, end):
        self.name = name
        self.status = status
        self.begin = begin
        self.end = end
        self.time_str = self.begin + '_' + self.end

    def summary(self):
        return self.name, self.status, self.begin, self.end


class MktInfo:
    def __init__(self, mkt):
        self.mkt = mkt
        self.timezone = ''
        self.basic_mkt_open_day_rule = ''
        self.period_dict_key_name = {}
        self.period_dict_key_time = {}
        self.config = None
        self.i18n_dict = None
        self.load_config('./configs/date_time/%s.cfg' % self.mkt)

    def load_config(self, config_path):
        # Loading from file
        if os.path.isfile(config_path):
            with open(config_path) as f:
                raw_config = f.readlines()
        else:
            # TODO: MQTT ERROR LOG
            print('File Not exist, ', config_path)
            raw_config = ''
        config = []
        for line in raw_config:
            if len(line.lstrip().rstrip()) > 0:
                tmp_line = line.split('#')[0].lstrip().rstrip()
                split_line = re.split(r'[ \t]+', tmp_line)
                if (split_line[0] != '') & (split_line[0] != '#'):
                    config.append(split_line)
        self.config = config
        # Parsing
        i18n_dict = {}
        for (idx, line) in enumerate(self.config):
            if line[0] == 'MARKET':
                self.mkt = line[1]
            elif line[0] == 'TIME_ZONE':
                self.timezone = line[1]
            elif line[0] == 'BASIC_OPEN_DATE':
                self.basic_mkt_open_day_rule = line[1]
            elif line[0] == 'PERIOD':
                name = line[1]
                status = self.config[idx + 1][1]
                begin = self.config[idx + 2][1]
                end = self.config[idx + 3][1]
                new_period = Period(name, status, begin, end)
                self.period_dict_key_name[name] = new_period
                self.period_dict_key_time[new_period.time_str] = new_period
            elif line[0] == 'I18N':
                key = line[1]
                translate_dict = {}
                for i in line[2:]:
                    lang = i.split(':')[0]
                    trans = i.split(':')[1]
                    translate_dict[lang] = trans
                i18n_dict[key] = translate_dict
        self.i18n_dict = i18n_dict

    def generate_calendar(self, start, end):
        spec_open_list = self.load_special_date_file('./configs/date_time/special_dates/open/' + self.mkt)
        spec_close_list = self.load_special_date_file('./configs/date_time/special_dates/close/' + self.mkt)
        plain_weekday_list = generate_date_range(start, end, only='weekday')
        plain_weekend_list = generate_date_range(start, end, only='weekend')
        date_today = get_today(tz=self.timezone)
        history_open_list = []
        if start < date_today:
            if self.mkt == 'CHN':
                history_open_list = get_market_open_date_list_history_CHN()
            elif self.mkt == 'US':
                history_open_list = get_market_open_date_list_history_US()
            else:
                # TODO: New mtk method should be appended here
                pass
        calendar_wday = {i: {'mkt_open': True, 'weekday': True} for i in plain_weekday_list} \
            if self.basic_mkt_open_day_rule == 'WEEKDAY' else \
            {i: {'mkt_open': False, 'weekday': True} for i in plain_weekday_list}
        calendar_wend = {i: {'mkt_open': False, 'weekday': False} for i in plain_weekend_list}
        calendar = {**calendar_wday, **calendar_wend}
        for d in history_open_list:
            try:
                calendar[d]['mkt_open'] = True
            except KeyError:
                pass
        for d in spec_close_list:
            try:
                calendar[d]['mkt_open'] = False
            except KeyError:
                pass
        for d in spec_open_list:
            try:
                calendar[d]['mkt_open'] = True
            except KeyError:
                pass
        calendar_df = pd.DataFrame(
            [{'date': i, 'mkt_open': calendar[i]['mkt_open'], 'weekday': calendar[i]['weekday']} for i in
             calendar.keys()])
        calendar_df = calendar_df.sort_values(by='date')
        calendar_df.to_csv('./configs/date_time/calendar/%s.csv' % self.mkt, index=False)

    def load_special_date_file(self, path):
        if os.path.isfile(path):
            try:
                with open(path) as f:
                    raw_list = f.readlines()
            except Exception as e:
                raw_list = []
                # TODO: MQTT ERROR LOG
        else:
            raw_list = []
        date_list = [line.lstrip().rstrip() for line in raw_list if len(line.lstrip().rstrip()) > 0]
        return date_list


def get_trans(target, i18n_dict):
    # FIXME need more properly i18n support
    return i18n_dict[target][I18N]
