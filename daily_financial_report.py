#!/usr/bin/python3
import subprocess

import time
from datetime import datetime, timedelta

from common_func import get_today, get_time_of_a_day
from common_func import load_market_close_days_for_year

if __name__ == "__main__":
    while True:
        today = get_today()
        close_days = load_market_close_days_for_year('2017')
        if today not in close_days:
            subprocess.call("./daily_update.py", shell=True)
            subprocess.call("./qa_trend_continue.py 100 5 %s" % get_today(), shell=True)

            subprocess.call("./send_mail.py -s 'zzy6548@126.com' '连续五日日平均交易价格趋势 %s' "
                            "'../stock_data/report/five_days_trend/%s.txt'" % (get_today(), get_today()), shell=True)
        next_wake_up_time = datetime(int(today.split('-')[0]), int(today.split('-')[1]), int(today.split('-')[2]), 21,
                                     35, 00) + timedelta(days=1)
        seconds = next_wake_up_time - datetime.now()
        print(get_time_of_a_day())
        time.sleep(seconds.seconds)
