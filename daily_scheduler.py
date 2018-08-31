# -*- coding: utf-8 -*-
import os
import schedule
import time
from tools.date_util.market_calendar_cn import MktCalendar

# DEPENDENCY( schedule )
cal = MktCalendar()


# TODO a good scheduler should read scheduled tasks from a config file and much better than this garbage.

def daily_job():
    """
    put all jobs you want to do everyday at 04:00 local time where local means your computer is.
    """
    if cal.quick_dict[cal.now('d')]['mkt_open']:
        os.system('./daily.sh')
    if cal.now('d').split("-")[2] == "28":
        cal.fetch_calendar()


if __name__ == '__main__':
    schedule.every().day.at("08:00").do(daily_job)
    while True:
        schedule.run_pending()
        time.sleep(1)
