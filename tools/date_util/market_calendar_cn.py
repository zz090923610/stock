import os

import pandas as pd
from tushare import trade_cal
from tushare.util.dateu import last_tddate

from configs.path import DIRs
from tools.io import test_internet, out
import tushare as ts
import time
import pytz

class MktCalendar:
    # DEPENDENCY( tushare pytz )
    def __init__(self, tz='Asia/Shanghai', mkt='CN'):
        self.timezone = tz
        self.market = mkt
        self.cal_path = os.path.join(DIRs.get("CALENDAR"), "%s.csv" % self.market)
        self.cal = self.load_calendar()
        self.quick_dict = self.build_quick_dict()

    def load_calendar(self):
        try:
            return pd.read_csv(self.cal_path)
        except FileNotFoundError:
            a = trade_cal()
            a.to_csv(self.cal_path, index=False)
            return a
        except Exception as e:
            out("mkt_calendar", 'Load calendar failed %s' %e)
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

    def _get_today(self):
        """
        return today's date in YYYY-MM-DD format
        :param tz: time zone
        :return: string
        """
        from datetime import datetime
        current_time = time.time()
        utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
        local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.timezone))
        local_today = local_now.strftime("%Y-%m-%d")
        return local_today

    def gen_date_list(self, goal, t='TODAY', in_mkt=False):
        # TODO
        if goal == "T" and t == 'TODAY':
            return [self._get_today()] if not in_mkt else [last_tddate()]

    def validate_date(self, day):
        if day == "TODAY":
            today = self._get_today()
            return today if self.quick_dict[today] == 1 else last_tddate()
        else:
            return day #FIXME
