# -*- coding: utf-8 -*-
import os
import schedule
import time
from tools.date_util.market_calendar_cn import MktCalendar

# DEPENDENCY( schedule )
cal = MktCalendar()


# TODO a good scheduler should read scheduled tasks cmd from a config file, with proper

def daily_job():
    if cal.quick_dict[cal.get_local_date()]:
        os.system('./daily.sh')
    if cal.get_local_date().split("-")[2] == "28":
        cal.update_calendar()


if __name__ == '__main__':
    schedule.every().day.at("04:00").do(daily_job)
    while True:
        schedule.run_pending()
        time.sleep(1)
