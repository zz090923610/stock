# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED


import os
import time
from datetime import datetime
import pandas as pd
import pytz
import tushare as ts
import re

from configs.conf import TUSHARE_PRO_TOKEN
from tools.data.file_hdl import load_pickle, save_pickle
from tools.data.path_hdl import path_expand, directory_ensure, file_exist
from tools.io import logging


# REGDIR( calendar )


# noinspection PyBroadException,PyUnusedLocal
class MktCalendar:
    """
    Market Calendar is a fundamental module of the whole project. Say if you want to get tick data 20 trade days ago,
    or if you want to predict stock price 3 trade days later given a predict function. This class maintain a market
    calendar and can return all kind of date/time described by functions or constants.
    """

    # DEPENDENCY( tushare pytz )
    def __init__(self, tz='Asia/Shanghai', mkt='CN'):
        """
        Within the scope of MktCalendar of CN, we define "local timezone" as 'Asia/Shanghai'
        :param tz:      timezone
        :param mkt:     stock market
        """
        # currently only considered tz='Asia/Shanghai', mkt='CN'
        # calendar fetched using tushare.
        # important: need to call load_calendar() after creating new instance.
        self.timezone = tz
        self.market = mkt

        directory_ensure(path_expand('calendar'))
        self.path_full_cal = os.path.join(path_expand('calendar'), "%s.csv" % self.market)
        self.path_trade_cal = os.path.join(path_expand('calendar'), "%s_trade.csv" % self.market)
        self.path_quick_dict = os.path.join(path_expand('calendar'), "%s_quick_dict.pickle" % self.market)
        self.path_lr_pair_list = os.path.join(path_expand('calendar'), "%s_lr_pair_list.pickle" % self.market)
        self.path_lr_pair_dict = os.path.join(path_expand('calendar'), "%s_lr_pair_dict.pickle" % self.market)

        self.date_boundary = (None, None)
        self.full_cal = None
        self.trade_cal = None
        self.quick_dict = None
        self.load_calendar()

        self.lr_pair_list = []
        self.lr_pair_dict = {}
        self.load_lr_pair()

    def now(self, ret_format='dt'):
        """
        return current date or time within self.timezone
        :param ret_format: 'YYYY-MM-DD' given 'd', 'HH:MM:SS' given 't', 'YYYY-MM-DD&HH:MM:SS' given 'dt'
        :return: current date&time in string format
        """
        from datetime import datetime
        current_time = time.time()
        utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
        local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.timezone))
        if ret_format == 'd':
            return local_now.strftime("%Y-%m-%d")
        elif ret_format == 't':
            return local_now.strftime("%H:%M:%S")
        else:  # format == 'dt'
            return local_now.strftime("%Y-%m-%d&%H:%M:%S")

    def neighbor_trade_date(self, of_which_idx, direction):
        """
        Given an index of date in full_calendar, return neighbor trade date of it.
        :param of_which_idx:    int
        :param direction:       string, prev or next
        :return:                string, YYYY-MM-DD
        """
        idx = of_which_idx
        while True:
            if direction == 'prev':
                idx -= 1
            else:  # direction == 'next'
                idx += 1
            if (idx < 0) | (idx >= len(self.full_cal.index)):
                return None
            if self.full_cal.iloc[idx]['mkt_open']:
                return self.full_cal.iloc[idx]['date']

    def neighbor_trade_date_given_date(self, of_which_date, direction):
        """
        Given an date, return neighbor trade date of it.
        :param of_which_date:   string, YYYY-MM-DD
        :param direction:       string, prev or next
        :return:                string, YYYY-MM-DD
        """
        try:
            idx = self.full_cal[of_which_date]['idx_full_cal']
            return self.neighbor_trade_date(idx, direction)
        except Exception as e:
            logging('MktCalendar', "[ ERROR ] neighbor_trade_date_given_date %s" % e, method='all')

    def fetch_calendar(self):
        """
        Fetch market calendar from tushare source
        """
        token = TUSHARE_PRO_TOKEN
        ts.set_token(token)
        pro = ts.pro_api()
        self.full_cal = pro.query('trade_cal', start_date='19900101', end_date='20171231')
        continue_cal = pro.query('trade_cal', start_date='20180101', end_date='20211231')
        self.full_cal = pd.concat([self.full_cal, continue_cal])
        self.full_cal.rename(columns={'cal_date': 'date', 'is_open': 'mkt_open'}, inplace=True)
        self.full_cal['date'] = self.full_cal['date'].apply(lambda x: x[0:4] + "-" + x[4:6] + "-" + x[6:8])
        self.trade_cal = self.full_cal[self.full_cal['mkt_open'] == 1].reset_index().drop(['index'], axis=1)

        self.full_cal['index'] = self.full_cal.index  # add this column to get a universal fetching routine
        self.trade_cal['index'] = self.trade_cal.index
        self.date_boundary = (self.full_cal['date'].tolist()[0], self.full_cal['date'].tolist()[-1])
        self.full_cal.to_csv(self.path_full_cal, index=False)
        self.trade_cal.to_csv(self.path_trade_cal, index=False)

    def build_quick_dict(self):
        """
        once quick_dict is built, you can search 'mkt_open', 'idx_full_cal', 'idx_trade_cal', 'prev_trade_date',
        'next_trade_date' of a specified date YYYY-MM-DD.
        Should only be called after fetch_calendar
        """
        # keys: mkt_open, idx_full_cal, idx_trade_cal, prev_trade_date, next_trade_date
        self.quick_dict = {}
        row_len = len(self.full_cal.index)
        for idx in range(0, row_len):
            logging('MktCalendar', "[ INFO ] build quick dict %d/%d" % (idx + 1, row_len), method='all')
            date = self.full_cal.iloc[idx]['date']
            mkt_open = self.full_cal.iloc[idx]['mkt_open']
            idx_full_cal = self.full_cal.iloc[idx]['index']
            idx_trade_cal = -1 if mkt_open == 0 else self.trade_cal[self.trade_cal['date'] == date].iloc[0]['index']
            prev_trade_date = self.neighbor_trade_date(idx_full_cal, 'prev')
            next_trade_date = self.neighbor_trade_date(idx_full_cal, 'next')
            self.quick_dict[date] = {'mkt_open': mkt_open, 'idx_full_cal': idx_full_cal,
                                     'idx_trade_cal': idx_trade_cal, 'prev_trade_date': prev_trade_date,
                                     'next_trade_date': next_trade_date}
        save_pickle(self.quick_dict, self.path_quick_dict)

    def load_calendar(self):
        """
        Load calendar.
        """
        if not file_exist(self.path_full_cal) & file_exist(self.path_trade_cal) & file_exist(self.path_quick_dict):
            self.fetch_calendar()
            self.build_quick_dict()
        try:
            self.full_cal = pd.read_csv(self.path_full_cal)
            self.trade_cal = pd.read_csv(self.path_trade_cal)
            self.quick_dict = load_pickle(self.path_quick_dict)
            self.date_boundary = (self.full_cal['date'].tolist()[0], self.full_cal['date'].tolist()[-1])
        except Exception as e:  # calendar files broken, re-fetch and rebuild everything
            logging("MktCalendar", "[ INFO ] Rebuild calendar...", method='all')
            self.fetch_calendar()
            self.build_quick_dict()

    def load_lr_pair(self):
        """
        lr_pair contains information to calculate how many seconds between 2 given time, pretty useful for mkt_monitor.
        """
        if not file_exist(self.path_lr_pair_dict) & file_exist(self.path_lr_pair_list):
            self.generate_lr_pair()
        try:
            self.lr_pair_dict = load_pickle(self.path_lr_pair_dict)
            self.lr_pair_list = load_pickle(self.path_lr_pair_list)
        except Exception as e:
            logging("MktCalendar", "[ INFO ] Rebuild LR-Pairs", method='all')
            self.generate_lr_pair()

    def generate_lr_pair(self):
        """
        lr_pair contains information to calculate how many seconds between 2 given time, pretty useful for mkt_monitor.
        should only be called after fetch_calendar
        """
        trade_date_list = self.full_cal[self.full_cal['mkt_open'] == 1]['date'].tolist()
        tl = ["09:30:00", "11:30:00", "13:00:00", "15:00:00"]
        open_from = ["09:30:00", "13:00:00"]
        close_from = ["11:30:00", "15:00:00"]
        day_pair_list = []
        for i in trade_date_list:
            day_pair = [(i, t) for t in tl]
            day_pair_list += day_pair

        while len(day_pair_list) > 1:
            pair_l = day_pair_list.pop(0)
            pair_r = day_pair_list.pop(0)
            date_time_format = '%Y-%m-%d&%H:%M:%S'

            secs = int(
                (datetime.strptime("%s&%s" % pair_r, date_time_format) -
                 datetime.strptime("%s&%s" % pair_l, date_time_format)).total_seconds())

            if (pair_l[1] in open_from) & (pair_r[1] in close_from):
                period_open = True
            else:  # should hold if data in good shape
                period_open = False
            self.lr_pair_list.append(("%s&%s" % pair_l, "%s&%s" % pair_r, period_open, secs))
            # ('%Y-%m-%d&%H:%M:%S', '%Y-%m-%d&%H:%M:%S', True, 7200)
            day_pair_list.insert(0, pair_r)

        for (idx, i) in enumerate(self.lr_pair_list):
            k = (i[0], i[1])
            v = (idx, i[2], i[3])
            self.lr_pair_dict[k] = v
        save_pickle(self.lr_pair_list, self.path_lr_pair_list)
        save_pickle(self.lr_pair_dict, self.path_lr_pair_dict)

    def search(self, date, key):
        """
        given a date, search it's property specified by key.
        :param date:    string, YYYY-MM-DD
        :param key:     'mkt_open', 'idx_full_cal', 'idx_trade_cal', 'prev_trade_date', 'next_trade_date'
        :return:        string, int, None
        """
        try:
            return self.quick_dict[date][key]
        except Exception as e:
            logging('MktCalendar', '[ ERROR ] date:%s or key:%s not in dict' % (date, key))
            return None

    def gen_date_list_given_range(self, start, end, trade_date_only=True):
        """
        given a start date and end date, return a list of dates between them.
        :param start:   string, YYYY-MM-DD
        :param end:     string, YYYY-MM-DD
        :param trade_date_only: boolean
        :return:        [] of YYYY-MM-DD
        """
        idx_start = self.search(start, 'idx_full_cal')
        idx_end = self.search(end, 'idx_full_cal')
        if trade_date_only:
            if self.full_cal.iloc[idx_start]['mkt_open']:
                idx_start = self.search(start, 'idx_trade_cal')
            else:
                next_trade_date = self.search(start, 'next_trade_date')
                idx_start = self.search(next_trade_date, 'idx_trade_cal')
            if self.full_cal.iloc[idx_end]['mkt_open']:
                idx_end = self.search(end, 'idx_trade_cal')
            else:
                prev_trade_date = self.search(end, 'prev_trade_date')
                idx_end = self.search(prev_trade_date, 'idx_trade_cal')
            df = self.trade_cal[self.trade_cal['index'] >= idx_start]
            df = df[df['index'] <= idx_end]
            return df['date'].tolist()
        else:
            df = self.full_cal[self.full_cal['index'] >= idx_start]
            df = df[df['index'] <= idx_end]
            return df['date'].tolist()

    def parse_date(self, day):
        """
        a date can be describe as TODAY, LASTCLOSEDTRADEDAY, t, T, T+5, t-10,
        this function return a proper TRADE DATE YYYY-MM-DD string of it.
        :param day:     date description, TODAY, LASTCLOSEDTRADEDAY, t, T, T+5, t-10, etc.
        :return:        YYYY-MM-DD on Trade Date Calendar which fits it.
        """
        if (day == "TODAY") | (day == 't') | (day == 'T'):
            local_date_now = self.now('d')
            return local_date_now if self.quick_dict[local_date_now]['mkt_open'] == 1 else \
                self.quick_dict[local_date_now]['prev_trade_date']
        elif day == "LASTCLOSEDTRADEDAY":
            local_date_now = self.now('d')
            local_time_now = self.now('t')
            return local_date_now if self.quick_dict[local_date_now]['mkt_open'] == 1 and local_time_now >= '15:05:00' \
                else self.quick_dict[local_date_now]['prev_trade_date']
        elif re.search(r'(\d\d\d\d-\d\d-\d\d)[ \t]*([-+])[ \t]*([\d]+)', day) is not None:
            try:
                res = re.search(r'(\d\d\d\d-\d\d-\d\d)[ \t]*([-+])[ \t]*([\d]+)', day)
                start = res.group(1)
                oper = res.group(2)
                offset = int(res.group(3))
                return self.calc_t(start, oper, offset)
            except Exception as e:
                logging("MktCalendar", "[ ERROR ] parse_date %s %s" % (day, e))
                return None
        elif re.search(r'[tT][ \t]*([-+])[ \t]*([\d]+)', day) is not None:
            res = re.search(r'[tT][ \t]*([-+])[ \t]*([\d]+)', day)
            start = self.now('d')
            oper = res.group(1)
            offset = int(res.group(2))
            return self.calc_t(start, oper, offset)
        else:
            return day

    def expand_date_in_str(self, target_str):
        """
        given a string, search date descriptions enclosed by {{}} and replace them with a valid YYYY-MM-DD on trade date
        calendar.
        :param target_str:  string
        :return:            string, YYYY-MM-DD
        """
        if re.search(r'{{TODAY}}|{{[tT]}}', target_str) is not None:
            local_date_now = self.now('d')
            str_today = local_date_now if self.quick_dict[local_date_now]['mkt_open'] == 1 else \
                self.quick_dict[local_date_now]['prev_trade_date']
            return re.sub(r"{{TODAY}}|{{[tT]}}", str_today, target_str)
        elif re.search(r'{{LASTCLOSEDTRADEDAY}}', target_str) is not None:
            local_date_now = self.now('d')
            local_time_now = self.now('t')
            str_today = local_date_now \
                if self.quick_dict[local_date_now]['mkt_open'] == 1 and local_time_now >= '15:05:00' \
                else self.quick_dict[local_date_now]['prev_trade_date']
            return re.sub(r"{{LASTCLOSEDTRADEDAY}}", str_today, target_str)
        elif re.search(r'{{(\d\d\d\d-\d\d-\d\d)[ \t]*([-+])[ \t]*([\d]+)}}', target_str) is not None:
            # something like "2018-01-01-5", "2018-01-01+7"
            res = re.search(r'{{(\d\d\d\d-\d\d-\d\d)[ \t]*([-+])[ \t]*([\d]+)}}', target_str)
            start = res.group(1)
            oper = res.group(2)
            offset = int(res.group(3))
            str_date = self.calc_t(start, oper, offset)
            return re.sub(r'{{(\d\d\d\d-\d\d-\d\d)[ \t]*([-+])[ \t]*([\d]+)}}', str_date, target_str)
        elif re.search(r'{{[tT][ \t]*([-+])[ \t]*([\d]+)}}', target_str) is not None:
            # something like "T-4", "t+3"
            res = re.search(r'{{[tT][ \t]*([-+])[ \t]*([\d]+)}}', target_str)
            start = self.now('d')
            oper = res.group(1)
            offset = int(res.group(2))
            str_date = self.calc_t(start, oper, offset)
            return re.sub(r'{{[tT][ \t]*([-+])[ \t]*([\d]+)}}', str_date, target_str)
        else:
            return target_str

    def calc_t(self, start, oper, offset):
        """
        return  start_date +- offset(days) in trade date calendar
        :param start:   string, YYYY-MM-DD
        :param oper:    string, + or -
        :param offset:  int
        :return:
        """
        try:
            if self.search(start, 'mkt_open'):
                idx_start = self.search(start, 'idx_trade_cal')
                return self.trade_cal.iloc[idx_start + offset]['date'] if oper == '+' else \
                    self.trade_cal.iloc[idx_start - offset]['date']
            else:
                if oper == '+':
                    idx_start = self.search(self.search(start, 'prev_trade_date'), 'idx_trade_cal')
                    return self.trade_cal.iloc[idx_start + offset]['date']
                else:
                    idx_start = self.search(self.search(start, 'next_trade_date'), 'idx_trade_cal')
                    return self.trade_cal.iloc[idx_start - offset]['date']
        except Exception as e:
            logging("MktCalendar", "[ ERROR ] calc_t %s%s%d %s" % (start, oper, offset, e))
            return start


# noinspection PyUnusedLocal
class MktDateTime:
    """
    Important for mkt_monitor. calc how many seconds the market is open between two given time.
    """

    def __init__(self, datetime_specified, calendar: MktCalendar):
        """
        :param datetime_specified: string, YYYY-MM-DD&HH:mm:SS
        :param calendar:           a instance of MktCalendar, fully loaded and updated.
        """
        self.datetime_specified = datetime_specified
        self.datetime_l = ""
        self.datetime_r = ""
        self.sec_to_l = 0
        self.sec_to_r = 0
        self.lr_pair = None
        self.equiv_date = self.is_in_mkt_close_period(datetime_specified, calendar)
        self.lr_init(calendar)
        self.cal = calendar
        self.calc_sec_to_lr()

    def lr_init(self, calendar: MktCalendar):
        """
        initialize lr pair of MktDateTime
        :param calendar:    a instance of MktCalendar, fully loaded and updated.
        """
        # should be call with valid self.datetime_specified
        # should be called after init self.equiv_date.
        (d, t) = self.split_date_time(self.datetime_specified)
        if self.equiv_date:
            if calendar.search(d, 'mkt_open') == 0:
                # d is not a trade day, navigate to prev, next trade day
                d_l = calendar.search(d, 'prev_trade_date')
                d_r = calendar.search(d, 'next_trade_date')
                t_l = "15:00:00"
                t_r = "09:30:00"
            else:
                # d is a trade day
                if ("00:00:00" <= t) & (t <= "09:30:00"):
                    # before mkt open
                    d_l = calendar.search(d, 'prev_trade_date')
                    d_r = d
                    t_l = "15:00:00"
                    t_r = "09:30:00"
                elif ("11:30:00" <= t) & (t <= "13:00:00"):
                    # lunch break
                    d_l = d
                    d_r = d
                    t_l = "11:30:00"
                    t_r = "13:00:00"
                elif ("15:00:00" <= t) & (t < "24:00:00"):
                    # after mkt close
                    d_l = d
                    d_r = calendar.search(d, 'next_trade_date')
                    t_l = "15:00:00"
                    t_r = "09:30:00"
                else:
                    d_l = d
                    d_r = d
                    t_l = t
                    t_r = t
        else:
            if ("09:30:00" < t) & (t < "11:30:00"):
                d_l = d
                d_r = d
                t_l = "09:30:00"
                t_r = "11:30:00"
            elif ("13:00:00" < t) & (t < "15:00:00"):
                d_l = d
                d_r = d
                t_l = "13:00:00"
                t_r = "15:00:00"
            else:
                d_l = d
                d_r = d
                t_l = t
                t_r = t
        self.datetime_l = "%s&%s" % (d_l, t_l)
        self.datetime_r = "%s&%s" % (d_r, t_r)
        self.lr_pair = (self.datetime_l, self.datetime_r)

    def calc_sec_to_lr(self):
        """
        calculate how many seconds between self and it's left right pair time.
        """
        # should be called after lr_init
        if self.equiv_date:
            self.sec_to_l = 0
            self.sec_to_r = 0
        else:
            date_time_format = '%Y-%m-%d&%H:%M:%S'
            self.sec_to_l = int(
                (datetime.strptime(self.datetime_specified, date_time_format) -
                 datetime.strptime(self.datetime_l, date_time_format)).total_seconds())
            self.sec_to_r = int(
                (datetime.strptime(self.datetime_r, date_time_format) -
                 datetime.strptime(self.datetime_specified, date_time_format)).total_seconds())

    def secs_to(self, target):
        """
        calc how many seconds from this to target time.
        :param target:  string, YYYY-MM-DD&HH:mm:SS
        :return:
        """
        date_time_format = '%Y-%m-%d&%H:%M:%S'
        return int(
            (datetime.strptime(target, date_time_format) - datetime.strptime(self.datetime_specified,
                                                                             date_time_format)).total_seconds())

    # noinspection PyBroadException,PyMethodMayBeStatic
    def split_date_time(self, target):
        """
        given a YYYY-MM-DD&HH:mm:SS, return (YYYY-MM-DD, HH:mm:SS)
        :param target: string
        :return: set of 2 strings
        """
        try:
            (d, t) = target.split("&")
        except Exception as e:
            (d, t) = ('', '')
        return d, t

    def is_in_mkt_close_period(self, target, calendar: MktCalendar) -> bool:
        """
        check whether target time is within market closed period
        :param target:      YYYY-MM-DD&HH:mm:SS
        :param calendar:    a instance of MktCalendar, fully loaded and updated.
        :return:            boolean
        """
        (d, t) = self.split_date_time(target)
        if calendar.search(d, 'mkt_open') == 0:
            return True
        else:
            if ("00:00:00" <= t) & (t <= "09:30:00"):
                return True
            elif ("11:30:00" <= t) & (t <= "13:00:00"):
                return True
            elif ("15:00:00" <= t) & (t < "24:00:00"):
                return True
            else:
                return False

    def __sub__(self, other):
        """
        calculate how many market open seconds between 2 MktDateTime instances.
        :param other:   another MktDateTime instance
        :return:        seconds, int
        """
        a = self.datetime_specified
        b = other.datetime_specified
        if a >= b:
            positive = True
        else:
            positive = False
        large = self if positive else other
        small = other if positive else self

        large_lr_pair = (large.datetime_l, large.datetime_r)
        small_lr_pair = (small.datetime_l, small.datetime_r)
        large_idx = self.cal.lr_pair_dict[large_lr_pair][0]
        small_idx = self.cal.lr_pair_dict[small_lr_pair][0]

        if small_idx != large_idx:
            secs = small.sec_to_r
            for idx in range(small_idx + 1, large_idx):
                if self.cal.lr_pair_list[idx][2]:
                    secs += self.cal.lr_pair_list[idx][3]
            secs += large.sec_to_l
        else:
            secs = small.sec_to_r - large.sec_to_r

        if positive:
            return secs
        else:
            return -1 * secs
