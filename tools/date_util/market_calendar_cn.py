# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED


import os
import time
from datetime import datetime

import pandas as pd
import pytz
from tushare import trade_cal

# DIRREG( calendar )
from tools.data.path_hdl import path_expand, directory_ensure


class MktCalendar:
    # DEPENDENCY( tushare pytz )
    # TODO: generate calendar if not exist
    def __init__(self, tz='Asia/Shanghai', mkt='CN'):
        self.timezone = tz
        self.market = mkt
        try:

            self.cal_path = os.path.join(path_expand('calendar'), "%s.csv" % self.market)
            directory_ensure(path_expand('calendar'))
        except Exception as e:
            self.cal_path = "%s.csv" % self.market
        self.cal = self.load_calendar()
        self.cal_open = self.cal[self.cal['isOpen'] == 1].reset_index()
        self.quick_dict = self.build_quick_dict()
        self.lr_pair_list = []
        self.lr_pair_dict = {}
        self.generate_lr_pair()

    def load_calendar(self):
        try:
            return pd.read_csv(self.cal_path)
        except FileNotFoundError:
            a = trade_cal()
            a.to_csv(self.cal_path, index=False)
            return a
        except Exception as e:
            return None

    def build_quick_dict(self):
        list_of_dict = self.cal.to_dict('records')
        quick_dict = {}
        for l in list_of_dict:
            quick_dict[l['calendarDate']] = l['isOpen']
        return quick_dict

    def update_calendar(self):
        self.cal = trade_cal()
        self.cal.to_csv(self.cal_path, index=False)

    def _get_local_now(self):
        from datetime import datetime
        current_time = time.time()
        utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
        return utc_now.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.timezone))

    def get_local_date(self):
        """
        return today's date in YYYY-MM-DD format
        :return: string
        """
        local_now = self._get_local_now()
        local_today = local_now.strftime("%Y-%m-%d")
        return local_today

    def get_local_time(self):
        local_now = self._get_local_now()
        local_time = local_now.strftime("%H:%M:%S")
        return local_time

    def get_local_dt(self):
        local_now = self._get_local_now()
        local_today = local_now.strftime("%Y-%m-%d")
        local_time = local_now.strftime("%H:%M:%S")
        return "%s&%s" % (local_today, local_time)

    def gen_date_list(self, goal, t='TODAY', in_mkt=False):
        # TODO
        if goal == "T" and t == 'TODAY':
            return [self.get_local_date()] if not in_mkt else [self.get_last_trade_date()]

    def validate_date(self, day):
        if day == "TODAY":
            local_date_now = self.get_local_date()
            return local_date_now if self.quick_dict[local_date_now] == 1 else self.get_last_trade_date()
        if day == "LASTCLOSEDTRADEDAY":
            local_date_now = self.get_local_date()
            local_time_now = self.get_local_time()
            return local_date_now if self.quick_dict[local_date_now] == 1 and local_time_now >= '15:05:00' \
                else self.get_last_trade_date()
        else:  # TODO, implement t plus 12345
            return day  # FIXME

    def get_last_trade_date(self):
        local_date_now = self.get_local_date()
        local_time_now = self.get_local_time()
        idx = int(self.cal_open.index[self.cal_open['calendarDate'] == local_date_now].tolist()[0])
        idx = idx if idx >= 1 else 1

        return local_date_now if self.quick_dict[local_date_now] == 1 and local_time_now >= '15:05:00' \
            else self.cal_open.iloc[idx - 1]['calendarDate']

    def get_day(self, target, t='TODAY'):
        # TODO rewrite this, why so ugly....
        try:
            t = self.validate_date(t)
            req_ascending = True if '+' in target else False
            day_diff = target.split("+")[1] if req_ascending else target.split("-")[1]
            day_diff = int(day_diff)
            idx_start = self.cal.index[self.cal['calendarDate'] == t].tolist()[0]
            if self.quick_dict[t] == 1:
                cnt = 0
                loop_idx = 0
                while True:
                    if req_ascending:
                        target_date = self.cal.iloc[idx_start + loop_idx]['calendarDate']
                    else:
                        target_date = self.cal.iloc[idx_start - loop_idx]['calendarDate']
                    loop_idx += 1
                    if self.quick_dict[target_date]:
                        if cnt == day_diff:
                            break
                        else:
                            cnt += 1
                return target_date
            else:
                if day_diff == 0:
                    day_diff = 1
                    req_ascending = False
                cnt = 0
                loop_idx = 0
                while True:
                    if req_ascending:
                        target_date = self.cal.iloc[idx_start + loop_idx]['calendarDate']
                    else:
                        target_date = self.cal.iloc[idx_start - loop_idx]['calendarDate']
                    loop_idx += 1
                    if self.quick_dict[target_date]:
                        if cnt + 1 == day_diff:
                            break
                        else:
                            cnt += 1
                return target_date

        except Exception as e:
            print(e)
            return ''

    def generate_lr_pair(self):
        l = self.cal[self.cal['isOpen'] == 1]['calendarDate'].tolist()
        tl = ["09:30:00", "11:30:00", "13:00:00", "15:00:00"]
        open_from = ["09:30:00", "13:00:00"]
        close_from = ["11:30:00", "15:00:00"]
        day_pair_list = []
        for i in l:
            day_pair = [(i, t) for t in tl]
            day_pair_list += day_pair

        while len(day_pair_list) > 1:
            pair_l = day_pair_list.pop(0)
            pair_r = day_pair_list.pop(0)
            FMT = '%Y-%m-%d&%H:%M:%S'

            secs = int(
                (datetime.strptime("%s&%s" % pair_r, FMT) - datetime.strptime("%s&%s" % pair_l, FMT)).total_seconds())

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


class MktDateTime:
    def __init__(self, datetime_specified, calendar: MktCalendar):
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
        # should be call with valid self.datetime_specified
        # should be called after init self.equiv_date.
        (d, t) = self.split_date_time(self.datetime_specified)
        if self.equiv_date:
            if calendar.quick_dict[d] == 0:
                d_l = calendar.get_day("t-1", d)
                d_r = calendar.get_day("t+1", d)
                t_l = "15:00:00"
                t_r = "09:30:00"
            else:
                if ("00:00:00" <= t) & (t <= "09:30:00"):
                    d_l = calendar.get_day("t-1", d)
                    d_r = d
                    t_l = "15:00:00"
                    t_r = "09:30:00"
                elif ("11:30:00" <= t) & (t <= "13:00:00"):
                    d_l = d
                    d_r = d
                    t_l = "11:30:00"
                    t_r = "13:00:00"
                elif ("15:00:00" <= t) & (t < "24:00:00"):
                    d_l = d
                    d_r = calendar.get_day("t+1", d)
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
        # should be called after lr_init
        if self.equiv_date:
            self.sec_to_l = 0
            self.sec_to_r = 0
        else:
            FMT = '%Y-%m-%d&%H:%M:%S'
            self.sec_to_l = int(
                (datetime.strptime(self.datetime_specified, FMT) - datetime.strptime(self.datetime_l,
                                                                                     FMT)).total_seconds())
            self.sec_to_r = int(
                (datetime.strptime(self.datetime_r, FMT) - datetime.strptime(self.datetime_specified,
                                                                             FMT)).total_seconds())

    def secs_to(self, target):
        FMT = '%Y-%m-%d&%H:%M:%S'
        return int(
            (datetime.strptime(target, FMT) - datetime.strptime(self.datetime_specified,
                                                                FMT)).total_seconds())

    # noinspection PyBroadException,PyMethodMayBeStatic
    def split_date_time(self, target):
        try:
            (d, t) = target.split("&")
        except Exception as e:
            (d, t) = ('', '')
        return d, t

    def is_in_mkt_close_period(self, target, calendar: MktCalendar) -> bool:
        (d, t) = self.split_date_time(target)
        if calendar.quick_dict[d] == 0:
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
