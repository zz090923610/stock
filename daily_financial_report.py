#!/usr/bin/python3
import subprocess

import time
from datetime import datetime, timedelta

from common_func import get_today, get_time_of_a_day, get_time
from common_func import load_market_close_days_for_year
from data_announance_fetch import fetch_all_announcements

if __name__ == "__main__":
    while True:
        today = get_today()
        close_days = load_market_close_days_for_year('2017')
        next_wake_up_time = datetime(int(today.split('-')[0]), int(today.split('-')[1]), int(today.split('-')[2]), 23,
                                     15, 00) + timedelta(days=1)
        local_date = get_today()
        local_time = get_time_of_a_day()
        ln = datetime(int(local_date.split('-')[0]), int(local_date.split('-')[1]), int(local_date.split('-')[2]),
                      int(local_time.split(':')[0]), int(local_time.split(':')[1]), int(local_time.split(':')[2]))
        seconds = next_wake_up_time - ln
        print("now is " + get_time_of_a_day())
        print("sleeping %d" % seconds.seconds)
        time.sleep(seconds.seconds)
        if today not in close_days:
            subprocess.call("./daily_update.py", shell=True)
            a = fetch_all_announcements(today)
            subprocess.call("./qa_trend_continue.py 100 5 %s" % get_today(), shell=True)
            subprocess.call("./send_mail.py -s '610153443@qq.com' '连续五日日平均交易价格趋势 %s' "
                            "'../stock_data/report/five_days_trend/%s.txt'" % (get_today(), get_today()), shell=True)
            subprocess.call("./send_mail.py -s 'zzy6548@126.com' '连续五日日平均交易价格趋势 %s' "
                            "'../stock_data/report/five_days_trend/%s.txt'" % (get_today(), get_today()), shell=True)
